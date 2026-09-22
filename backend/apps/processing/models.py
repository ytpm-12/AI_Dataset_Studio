from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class ProcessingJob(models.Model):
    class Kind(models.TextChoices):
        PROFILE = 'profile', 'Dataset profiling'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='processing_jobs',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='processing_jobs',
        null=True,
        blank=True,
    )
    uploaded_file = models.ForeignKey(
        'datasets.UploadedFile',
        on_delete=models.CASCADE,
        related_name='processing_jobs',
    )
    kind = models.CharField(max_length=32, choices=Kind.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    progress = models.PositiveSmallIntegerField(
        default=0,
        validators=(MinValueValidator(0), MaxValueValidator(100)),
    )
    celery_task_id = models.CharField(max_length=255, blank=True, db_index=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at', '-id')
        indexes = (
            models.Index(fields=('owner', '-created_at')),
            models.Index(fields=('project', 'status')),
            models.Index(fields=('uploaded_file', 'kind')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('uploaded_file', 'kind'),
                condition=Q(status__in=('pending', 'processing')),
                name='unique_active_job_per_upload_kind',
            ),
            models.CheckConstraint(
                condition=Q(progress__gte=0, progress__lte=100),
                name='processing_job_progress_0_100',
            ),
        )

    def __str__(self):
        return f'{self.get_kind_display()} - {self.uploaded_file}'
