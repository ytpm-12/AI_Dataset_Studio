import json

import pandas as pd
from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException
from django.conf import settings
from django.utils import timezone

from .models import UploadedFile


class DatasetValidationError(ValueError):
    pass


def _dataframe_profile(frame, file_type, truncated=False):
    columns = []
    for index, column_name in enumerate(frame.columns):
        series = frame.iloc[:, index]
        missing_count = int(series.isna().sum())
        try:
            unique_count = int(series.nunique(dropna=True))
        except TypeError:
            unique_count = None

        sample_values = [
            str(value)
            for value in series.dropna().head(settings.PROFILE_SAMPLE_VALUES).tolist()
        ]
        columns.append(
            {
                'name': str(column_name),
                'dtype': str(series.dtype),
                'missing_count': missing_count,
                'missing_percentage': round(
                    (missing_count / len(frame) * 100) if len(frame) else 0,
                    2,
                ),
                'unique_count': unique_count,
                'sample_values': sample_values,
            }
        )

    return {
        'file_type': file_type,
        'rows_profiled': len(frame),
        'column_count': len(frame.columns),
        'truncated': truncated,
        'columns': columns,
    }


def _profile_csv(uploaded_file):
    uploaded_file.file.open('rb')
    try:
        frame = pd.read_csv(uploaded_file.file, nrows=settings.PROFILE_MAX_ROWS + 1)
    finally:
        uploaded_file.file.close()

    truncated = len(frame) > settings.PROFILE_MAX_ROWS
    frame = frame.head(settings.PROFILE_MAX_ROWS)
    if not len(frame.columns):
        raise DatasetValidationError('Le fichier CSV ne contient aucune colonne.')
    return _dataframe_profile(frame, UploadedFile.FileType.CSV, truncated)


def _profile_json(uploaded_file):
    uploaded_file.file.open('rb')
    try:
        raw_content = uploaded_file.file.read()
    finally:
        uploaded_file.file.close()

    payload = json.loads(raw_content.decode('utf-8-sig'))
    if isinstance(payload, list):
        truncated = len(payload) > settings.PROFILE_MAX_ROWS
        payload = payload[: settings.PROFILE_MAX_ROWS]
    else:
        truncated = False

    frame = pd.json_normalize(payload)
    if not len(frame.columns):
        raise DatasetValidationError('Le fichier JSON ne contient aucune donnée tabulaire.')
    return _dataframe_profile(frame, UploadedFile.FileType.JSON, truncated)


def _profile_xml(uploaded_file):
    uploaded_file.file.open('rb')
    try:
        root = ElementTree.parse(uploaded_file.file).getroot()
    finally:
        uploaded_file.file.close()

    records = []
    children = list(root)
    truncated = len(children) > settings.PROFILE_MAX_ROWS
    for element in children[: settings.PROFILE_MAX_ROWS]:
        nested = list(element)
        if nested:
            record = {child.tag: child.text for child in nested}
            record.update({f'@{key}': value for key, value in element.attrib.items()})
        else:
            record = {element.tag: element.text}
        records.append(record)

    if not records:
        raise DatasetValidationError('Le fichier XML ne contient aucun enregistrement.')
    frame = pd.DataFrame(records)
    return _dataframe_profile(frame, UploadedFile.FileType.XML, truncated)


PROFILERS = {
    UploadedFile.FileType.CSV: _profile_csv,
    UploadedFile.FileType.JSON: _profile_json,
    UploadedFile.FileType.XML: _profile_xml,
}


def validate_and_profile(uploaded_file, defer_large_files=True):
    synchronous_limit = settings.SYNC_PROFILE_MAX_MB * 1024 * 1024
    if defer_large_files and uploaded_file.size > synchronous_limit:
        uploaded_file.status = UploadedFile.Status.VALIDATION_PENDING
        uploaded_file.profile = {
            'deferred': True,
            'reason': 'file_exceeds_synchronous_profile_limit',
        }
        uploaded_file.validation_errors = []
        uploaded_file.validated_at = None
        uploaded_file.save(
            update_fields=('status', 'profile', 'validation_errors', 'validated_at', 'updated_at')
        )
        return uploaded_file

    try:
        uploaded_file.status = UploadedFile.Status.VALIDATION_PENDING
        uploaded_file.save(update_fields=('status', 'updated_at'))
        uploaded_file.profile = PROFILERS[uploaded_file.file_type](uploaded_file)
        uploaded_file.validation_errors = []
        uploaded_file.status = UploadedFile.Status.VALIDATED
    except (
        DatasetValidationError,
        DefusedXmlException,
        ElementTree.ParseError,
        json.JSONDecodeError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError,
    ) as exc:
        uploaded_file.profile = {}
        uploaded_file.validation_errors = [str(exc)]
        uploaded_file.status = UploadedFile.Status.INVALID

    uploaded_file.validated_at = timezone.now()
    uploaded_file.save(
        update_fields=(
            'status',
            'profile',
            'validation_errors',
            'validated_at',
            'updated_at',
        )
    )
    return uploaded_file
