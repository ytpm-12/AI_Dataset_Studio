import json
import re
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from apps.datasets.models import UploadedFile
from apps.datasets.preview import read_dataset_frame
from apps.datasets.profiling import validate_and_profile

from .models import Transformation


class DatasetTooLargeForSynchronousCleaning(ValueError):
    pass


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
            output_file = UploadedFile(
                owner=uploaded_file.owner,
                project=uploaded_file.project,
                name=f'{uploaded_file.name} · sans doublons',
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
