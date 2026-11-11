import json

import pandas as pd
from defusedxml import ElementTree

from .models import UploadedFile


def _read_csv(uploaded_file, row_count):
    uploaded_file.file.open('rb')
    try:
        return pd.read_csv(uploaded_file.file, nrows=row_count)
    finally:
        uploaded_file.file.close()


def _read_json(uploaded_file, row_count):
    uploaded_file.file.open('rb')
    try:
        payload = json.loads(uploaded_file.file.read().decode('utf-8-sig'))
    finally:
        uploaded_file.file.close()

    if isinstance(payload, list):
        payload = payload[:row_count]
    return pd.json_normalize(payload)


def _read_xml(uploaded_file, row_count):
    uploaded_file.file.open('rb')
    try:
        root = ElementTree.parse(uploaded_file.file).getroot()
    finally:
        uploaded_file.file.close()

    records = []
    for element in list(root)[:row_count]:
        nested = list(element)
        if nested:
            record = {child.tag: child.text for child in nested}
            record.update({f'@{key}': value for key, value in element.attrib.items()})
        else:
            record = {element.tag: element.text}
        records.append(record)
    return pd.DataFrame(records)


READERS = {
    UploadedFile.FileType.CSV: _read_csv,
    UploadedFile.FileType.JSON: _read_json,
    UploadedFile.FileType.XML: _read_xml,
}


def build_dataset_preview(uploaded_file, limit):
    frame = READERS[uploaded_file.file_type](uploaded_file, limit + 1)
    truncated = len(frame) > limit
    frame = frame.head(limit)

    # pandas.to_json normalise aussi les types numpy et remplace NaN par null.
    rows = json.loads(frame.to_json(orient='records', date_format='iso'))
    return {
        'columns': [str(column) for column in frame.columns],
        'rows': rows,
        'returned_rows': len(rows),
        'limit': limit,
        'truncated': truncated,
    }
