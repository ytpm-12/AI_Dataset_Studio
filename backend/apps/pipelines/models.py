from django.conf import settings
from django.db import models


class Transformation(models.Model):
    class Operation(models.TextChoices):
        REMOVE_EXACT_DUPLICATES = 'remove_exact_duplicates', 'Remove exact duplicates'
        HANDLE_MISSING_VALUES = 'handle_missing_values', 'Handle missing values'
        CONVERT_COLUMN_TYPE = 'convert_column_type', 'Convert column type'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dataset_transformations',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='transformations',
    )
    source_file = models.ForeignKey(
        'datasets.UploadedFile',
        on_delete=models.PROTECT,
        related_name='source_transformations',
    )
    output_file = models.OneToOneField(
        'datasets.UploadedFile',
        on_delete=models.PROTECT,
        related_name='output_transformation',
        null=True,
        blank=True,
    )
    operation = models.CharField(max_length=48, choices=Operation.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    parameters = models.JSONField(default=dict, blank=True)
    summary = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = (
            models.Index(fields=('owner', '-created_at')),
            models.Index(fields=('source_file', '-created_at')),
        )

    def __str__(self):
        return f'{self.get_operation_display()} - {self.source_file}'
