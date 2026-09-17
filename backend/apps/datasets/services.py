import hashlib
from pathlib import Path

from .models import UploadedFile


FILE_TYPE_BY_EXTENSION = {
    '.csv': UploadedFile.FileType.CSV,
    '.json': UploadedFile.FileType.JSON,
    '.xml': UploadedFile.FileType.XML,
}


def detect_file_type(filename):
    return FILE_TYPE_BY_EXTENSION.get(Path(filename).suffix.lower())


def compute_sha256(uploaded_file):
    current_position = uploaded_file.tell()
    uploaded_file.seek(0)

    digest = hashlib.sha256()
    for chunk in uploaded_file.chunks():
        digest.update(chunk)

    uploaded_file.seek(current_position)
    return digest.hexdigest()
