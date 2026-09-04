import uuid
from pathlib import Path

from django.conf import settings
from django.db import models


def dataset_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f'datasets/user_{instance.owner_id}/{uuid.uuid4().hex}{extension}'


class UploadedFile(models.Model):
    class FileType(models.TextChoices):
        CSV = 'csv', 'CSV'
        JSON = 'json', 'JSON'
        XML = 'xml', 'XML'
        PDF = 'pdf', 'PDF'
        IMAGE = 'image', 'Image'

    class Status(models.TextChoices):
        UPLOADED = 'uploaded', 'Uploaded'
        VALIDATION_PENDING = 'validation_pending', 'Validation pending'
        VALIDATED = 'validated', 'Validated'
        INVALID = 'invalid', 'Invalid'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_files',
    )
    name = models.CharField(max_length=180)
    file = models.FileField(upload_to=dataset_upload_path)
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=FileType.choices)
    content_type = models.CharField(max_length=120, blank=True)
    size = models.PositiveBigIntegerField()
    checksum_sha256 = models.CharField(max_length=64, blank=True)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.UPLOADED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['file_type']),
        ]

    def __str__(self):
        return self.name
