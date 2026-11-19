import json
import re
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree

import pandas as pd
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from apps.datasets.models import UploadedFile
from apps.datasets.preview import read_dataset_frame
from apps.datasets.profiling import validate_and_profile

from .models import Transformation


class DatasetTooLargeForSynchronousCleaning(ValueError):
    pass


MISSING_VALUE_STRATEGIES = {'drop_rows', 'constant', 'mean', 'median', 'mode'}
TARGET_TYPES = {'integer', 'float', 'string', 'boolean', 'datetime'}


def _comparable_value(value):
    if isinstance(value, (dict, list, tuple, set)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return value


def preview_exact_duplicates(uploaded_file, max_rows, sample_size=10):
    frame = read_dataset_frame(uploaded_file, max_rows + 1)
    truncated = len(frame) > max_rows
    frame = frame.head(max_rows)

    if frame.empty:
        return {
            'analyzed_rows': 0,
            'duplicate_rows': 0,
            'affected_rows': 0,
            'rows_after_cleanup': 0,
            'duplicate_percentage': 0,
            'sample_rows': [],
            'truncated': truncated,
        }

    comparable_frame = frame.map(_comparable_value)
    affected_mask = comparable_frame.duplicated(keep=False)
    removable_mask = comparable_frame.duplicated(keep='first')
    duplicate_rows = int(removable_mask.sum())
    affected_rows = int(affected_mask.sum())

    sample = frame.loc[affected_mask].head(sample_size).copy()
    sample.insert(0, '_row_number', sample.index + 1)
    sample_rows = json.loads(sample.to_json(orient='records', date_format='iso'))

    return {
        'analyzed_rows': len(frame),
        'duplicate_rows': duplicate_rows,
        'affected_rows': affected_rows,
        'rows_after_cleanup': len(frame) - duplicate_rows,
        'duplicate_percentage': round(
            (duplicate_rows / len(frame) * 100) if len(frame) else 0,
            2,
        ),
        'sample_rows': sample_rows,
        'truncated': truncated,
    }


def preview_missing_values(uploaded_file, max_rows):
    frame = read_dataset_frame(uploaded_file, max_rows + 1)
    truncated = len(frame) > max_rows
    frame = frame.head(max_rows)
    columns = []
    for column in frame.columns:
        missing_count = int(frame[column].isna().sum())
        columns.append(
            {
                'name': str(column),
                'dtype': str(frame[column].dtype),
                'missing_count': missing_count,
                'missing_percentage': round(
                    (missing_count / len(frame) * 100) if len(frame) else 0,
                    2,
                ),
                'numeric': bool(pd.api.types.is_numeric_dtype(frame[column])),
            }
        )
    return {
        'analyzed_rows': len(frame),
        'total_missing_values': int(frame.isna().sum().sum()),
        'columns': columns,
        'truncated': truncated,
        'strategies': sorted(MISSING_VALUE_STRATEGIES),
    }


def _serialize_frame(frame, file_type):
    if file_type == UploadedFile.FileType.CSV:
        return frame.to_csv(index=False).encode('utf-8-sig')
    if file_type == UploadedFile.FileType.JSON:
        return frame.to_json(orient='records', force_ascii=False, indent=2).encode('utf-8')
    if file_type == UploadedFile.FileType.XML:
        root = ElementTree.Element('dataset')
        for record in json.loads(frame.to_json(orient='records', date_format='iso')):
            row = ElementTree.SubElement(root, 'record')
            for column, value in record.items():
                if value is None:
                    continue
                if column.startswith('@'):
                    row.set(column[1:], str(value))
                    continue
                if not re.fullmatch(r'[A-Za-z_][\w.-]*', str(column)):
                    raise ValueError(f'La colonne {column!r} ne peut pas être exportée en XML.')
                child = ElementTree.SubElement(row, str(column))
                child.text = str(value)
        stream = BytesIO()
        ElementTree.ElementTree(root).write(stream, encoding='utf-8', xml_declaration=True)
        return stream.getvalue()
    raise ValueError('Format de fichier non supporté pour le nettoyage.')


def _create_output_dataset(uploaded_file, content, output_name, display_suffix):
    output_file = UploadedFile(
        owner=uploaded_file.owner,
        project=uploaded_file.project,
        name=f'{uploaded_file.name} · {display_suffix}',
        original_name=output_name,
        file_type=uploaded_file.file_type,
        content_type=uploaded_file.content_type,
        size=len(content),
        checksum_sha256=sha256(content).hexdigest(),
        status=UploadedFile.Status.UPLOADED,
    )
    output_file.file.save(output_name, ContentFile(content), save=False)
    output_file.save()
    validate_and_profile(output_file, defer_large_files=False)
    if output_file.status != UploadedFile.Status.VALIDATED:
        raise ValueError('Le fichier nettoyé généré ne passe pas la validation.')
    return output_file


def apply_exact_duplicate_removal(uploaded_file, max_rows):
    transformation = Transformation.objects.create(
        owner=uploaded_file.owner,
        project=uploaded_file.project,
        source_file=uploaded_file,
        operation=Transformation.Operation.REMOVE_EXACT_DUPLICATES,
        parameters={'keep': 'first', 'columns': 'all'},
    )
    output_file = None
    try:
        frame = read_dataset_frame(uploaded_file, max_rows + 1)
        if len(frame) > max_rows:
            raise DatasetTooLargeForSynchronousCleaning(
                "Le fichier dépasse la limite de nettoyage synchrone. Aucun changement n'a été appliqué."
            )

        cleaned_frame = frame.drop_duplicates(keep='first')
        removed_rows = len(frame) - len(cleaned_frame)
        content = _serialize_frame(cleaned_frame, uploaded_file.file_type)
        extension = Path(uploaded_file.original_name).suffix.lower()
        output_name = f'{Path(uploaded_file.original_name).stem}_deduplicated{extension}'

        with transaction.atomic():
            output_file = _create_output_dataset(
                uploaded_file, content, output_name, 'sans doublons'
            )

            transformation.output_file = output_file
            transformation.status = Transformation.Status.COMPLETED
            transformation.summary = {
                'input_rows': len(frame),
                'removed_rows': removed_rows,
                'output_rows': len(cleaned_frame),
            }
            transformation.completed_at = timezone.now()
            transformation.save(
                update_fields=('output_file', 'status', 'summary', 'completed_at')
            )
        return transformation
    except Exception as exc:
        if output_file and output_file.file:
            output_file.file.delete(save=False)
        transformation.status = Transformation.Status.FAILED
        transformation.error_message = str(exc)
        transformation.completed_at = timezone.now()
        transformation.save(update_fields=('status', 'error_message', 'completed_at'))
        raise


def apply_missing_value_treatment(uploaded_file, max_rows, column, strategy, value=None):
    if strategy not in MISSING_VALUE_STRATEGIES:
        raise ValueError('Stratégie de traitement des valeurs manquantes invalide.')
    transformation = Transformation.objects.create(
        owner=uploaded_file.owner,
        project=uploaded_file.project,
        source_file=uploaded_file,
        operation=Transformation.Operation.HANDLE_MISSING_VALUES,
        parameters={'column': column, 'strategy': strategy, 'value': value},
    )
    output_file = None
    try:
        frame = read_dataset_frame(uploaded_file, max_rows + 1)
        if len(frame) > max_rows:
            raise DatasetTooLargeForSynchronousCleaning(
                "Le fichier dépasse la limite de nettoyage synchrone. Aucun changement n'a été appliqué."
            )
        if column not in frame.columns:
            raise ValueError('La colonne sélectionnée est introuvable.')

        missing_before = int(frame[column].isna().sum())
        cleaned_frame = frame.copy()
        if strategy == 'drop_rows':
            cleaned_frame = cleaned_frame.dropna(subset=[column])
        elif strategy == 'constant':
            if value is None or value == '':
                raise ValueError('Une valeur de remplacement est obligatoire.')
            cleaned_frame[column] = cleaned_frame[column].fillna(value)
        elif strategy in {'mean', 'median'}:
            if not pd.api.types.is_numeric_dtype(cleaned_frame[column]):
                raise ValueError('La moyenne et la médiane exigent une colonne numérique.')
            replacement = (
                cleaned_frame[column].mean()
                if strategy == 'mean'
                else cleaned_frame[column].median()
            )
            if pd.isna(replacement):
                raise ValueError('La colonne ne contient aucune valeur permettant le calcul.')
            cleaned_frame[column] = cleaned_frame[column].fillna(replacement)
        else:
            modes = cleaned_frame[column].mode(dropna=True)
            if modes.empty:
                raise ValueError('La colonne ne contient aucune valeur fréquente utilisable.')
            cleaned_frame[column] = cleaned_frame[column].fillna(modes.iloc[0])

        content = _serialize_frame(cleaned_frame, uploaded_file.file_type)
        extension = Path(uploaded_file.original_name).suffix.lower()
        output_name = f'{Path(uploaded_file.original_name).stem}_missing_cleaned{extension}'
        with transaction.atomic():
            output_file = _create_output_dataset(
                uploaded_file, content, output_name, 'valeurs manquantes traitées'
            )
            transformation.output_file = output_file
            transformation.status = Transformation.Status.COMPLETED
            transformation.summary = {
                'input_rows': len(frame),
                'output_rows': len(cleaned_frame),
                'column': column,
                'missing_before': missing_before,
                'missing_after': int(cleaned_frame[column].isna().sum()),
                'removed_rows': len(frame) - len(cleaned_frame),
            }
            transformation.completed_at = timezone.now()
            transformation.save(
                update_fields=('output_file', 'status', 'summary', 'completed_at')
            )
        return transformation
    except Exception as exc:
        if output_file and output_file.file:
            output_file.file.delete(save=False)
        transformation.status = Transformation.Status.FAILED
        transformation.error_message = str(exc)
        transformation.completed_at = timezone.now()
        transformation.save(update_fields=('status', 'error_message', 'completed_at'))
        raise


def _convert_series(series, target_type):
    if target_type == 'integer':
        numeric = pd.to_numeric(series, errors='raise')
        non_null = numeric.dropna()
        if not ((non_null % 1) == 0).all():
            raise ValueError('Certaines valeurs décimales ne peuvent pas devenir des entiers.')
        return numeric.astype('Int64')
    if target_type == 'float':
        return pd.to_numeric(series, errors='raise').astype('Float64')
    if target_type == 'string':
        return series.astype('string')
    if target_type == 'datetime':
        return pd.to_datetime(series, errors='raise')
    if target_type == 'boolean':
        mapping = {
            'true': True, '1': True, 'yes': True, 'oui': True,
            'false': False, '0': False, 'no': False, 'non': False,
        }
        converted = series.map(
            lambda item: mapping.get(str(item).strip().lower()) if not pd.isna(item) else pd.NA
        )
        invalid = series.notna() & converted.isna()
        if invalid.any():
            raise ValueError('Certaines valeurs ne correspondent pas à un booléen reconnu.')
        return converted.astype('boolean')
    raise ValueError('Type cible invalide.')


def apply_type_conversion(uploaded_file, max_rows, column, target_type):
    if target_type not in TARGET_TYPES:
        raise ValueError('Type cible invalide.')
    transformation = Transformation.objects.create(
        owner=uploaded_file.owner,
        project=uploaded_file.project,
        source_file=uploaded_file,
        operation=Transformation.Operation.CONVERT_COLUMN_TYPE,
        parameters={'column': column, 'target_type': target_type},
    )
    output_file = None
    try:
        frame = read_dataset_frame(uploaded_file, max_rows + 1)
        if len(frame) > max_rows:
            raise DatasetTooLargeForSynchronousCleaning(
                "Le fichier dépasse la limite de nettoyage synchrone. Aucun changement n'a été appliqué."
            )
        if column not in frame.columns:
            raise ValueError('La colonne sélectionnée est introuvable.')
        source_type = str(frame[column].dtype)
        converted_frame = frame.copy()
        converted_frame[column] = _convert_series(converted_frame[column], target_type)
        content = _serialize_frame(converted_frame, uploaded_file.file_type)
        extension = Path(uploaded_file.original_name).suffix.lower()
        output_name = f'{Path(uploaded_file.original_name).stem}_{column}_{target_type}{extension}'
        with transaction.atomic():
            output_file = _create_output_dataset(
                uploaded_file, content, output_name, f'{column} convertie en {target_type}'
            )
            transformation.output_file = output_file
            transformation.status = Transformation.Status.COMPLETED
            transformation.summary = {
                'input_rows': len(frame),
                'output_rows': len(converted_frame),
                'column': column,
                'source_type': source_type,
                'target_type': target_type,
            }
            transformation.completed_at = timezone.now()
            transformation.save(
                update_fields=('output_file', 'status', 'summary', 'completed_at')
            )
        return transformation
    except Exception as exc:
        if output_file and output_file.file:
            output_file.file.delete(save=False)
        transformation.status = Transformation.Status.FAILED
        transformation.error_message = str(exc)
        transformation.completed_at = timezone.now()
        transformation.save(update_fields=('status', 'error_message', 'completed_at'))
        raise


def build_export(uploaded_file, target_format, max_rows):
    if target_format not in {'csv', 'json'}:
        raise ValueError("Le format d'export doit être csv ou json.")
    frame = read_dataset_frame(uploaded_file, max_rows + 1)
    if len(frame) > max_rows:
        raise DatasetTooLargeForSynchronousCleaning(
            "Le fichier dépasse la limite d'export synchrone."
        )
    if target_format == 'csv':
        return frame.to_csv(index=False).encode('utf-8-sig'), 'text/csv'
    return (
        frame.to_json(orient='records', force_ascii=False, indent=2).encode('utf-8'),
        'application/json',
    )


def build_quality_report(uploaded_file, max_rows):
    frame = read_dataset_frame(uploaded_file, max_rows + 1)
    truncated = len(frame) > max_rows
    frame = frame.head(max_rows)
    cells = len(frame) * len(frame.columns)
    missing_values = int(frame.isna().sum().sum())
    duplicate_rows = int(frame.map(_comparable_value).duplicated(keep='first').sum()) if len(frame) else 0
    missing_rate = (missing_values / cells * 100) if cells else 0
    duplicate_rate = (duplicate_rows / len(frame) * 100) if len(frame) else 0
    completeness_score = max(0, 100 - missing_rate)
    uniqueness_score = max(0, 100 - duplicate_rate)
    overall_score = round(completeness_score * 0.6 + uniqueness_score * 0.4, 2)
    return {
        'dataset_id': uploaded_file.pk,
        'analyzed_rows': len(frame),
        'column_count': len(frame.columns),
        'missing_values': missing_values,
        'missing_rate': round(missing_rate, 2),
        'duplicate_rows': duplicate_rows,
        'duplicate_rate': round(duplicate_rate, 2),
        'completeness_score': round(completeness_score, 2),
        'uniqueness_score': round(uniqueness_score, 2),
        'overall_score': overall_score,
        'truncated': truncated,
        'generated_at': timezone.now(),
    }
