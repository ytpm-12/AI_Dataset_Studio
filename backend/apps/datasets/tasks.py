import logging

from celery import shared_task
from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.processing.models import ProcessingJob

from .models import UploadedFile
from .profiling import validate_and_profile


logger = logging.getLogger(__name__)


def get_or_create_profile_job(uploaded_file):
    active_job = ProcessingJob.objects.filter(
        uploaded_file=uploaded_file,
        kind=ProcessingJob.Kind.PROFILE,
        status__in=(
            ProcessingJob.Status.PENDING,
            ProcessingJob.Status.PROCESSING,
        ),
    ).first()
    if active_job:
        return active_job

    try:
        return ProcessingJob.objects.create(
            owner=uploaded_file.owner,
            project=uploaded_file.project,
            uploaded_file=uploaded_file,
            kind=ProcessingJob.Kind.PROFILE,
        )
    except IntegrityError:
        return ProcessingJob.objects.get(
            uploaded_file=uploaded_file,
            kind=ProcessingJob.Kind.PROFILE,
            status__in=(
                ProcessingJob.Status.PENDING,
                ProcessingJob.Status.PROCESSING,
            ),
        )


def mark_job_started(job):
    job.status = ProcessingJob.Status.PROCESSING
    job.progress = 10
    job.attempts += 1
    job.error_message = ''
    job.started_at = job.started_at or timezone.now()
    job.finished_at = None
    job.save(
        update_fields=(
            'status',
            'progress',
            'attempts',
            'error_message',
            'started_at',
            'finished_at',
            'updated_at',
        )
    )


def mark_job_completed(job):
    job.status = ProcessingJob.Status.COMPLETED
    job.progress = 100
    job.error_message = ''
    job.finished_at = timezone.now()
    job.save(
        update_fields=(
            'status',
            'progress',
            'error_message',
            'finished_at',
            'updated_at',
        )
    )


def mark_job_failed(job):
    job.status = ProcessingJob.Status.FAILED
    job.error_message = 'Le traitement a échoué en raison d’une erreur interne.'
    job.finished_at = timezone.now()
    job.save(
        update_fields=(
            'status',
            'error_message',
            'finished_at',
            'updated_at',
        )
    )


@shared_task(ignore_result=False)
def profile_uploaded_file(uploaded_file_id, processing_job_id=None):
    try:
        uploaded_file = UploadedFile.objects.select_related('owner', 'project').get(
            pk=uploaded_file_id
        )
    except UploadedFile.DoesNotExist:
        return {'status': 'missing', 'uploaded_file_id': uploaded_file_id}

    job = (
        ProcessingJob.objects.filter(pk=processing_job_id).first()
        if processing_job_id
        else get_or_create_profile_job(uploaded_file)
    )
    if job is None or job.uploaded_file_id != uploaded_file.id:
        return {'status': 'missing_job', 'uploaded_file_id': uploaded_file_id}

    with transaction.atomic():
        job = ProcessingJob.objects.select_for_update().get(pk=job.pk)
        uploaded_file = UploadedFile.objects.select_for_update().get(
            pk=uploaded_file_id
        )

        if job.status in {
            ProcessingJob.Status.PROCESSING,
            ProcessingJob.Status.COMPLETED,
            ProcessingJob.Status.CANCELLED,
        }:
            return {
                'status': job.status,
                'uploaded_file_id': uploaded_file_id,
                'processing_job_id': job.pk,
            }

        if uploaded_file.status in {
            UploadedFile.Status.VALIDATED,
            UploadedFile.Status.INVALID,
        }:
            mark_job_completed(job)
            return {
                'status': uploaded_file.status,
                'uploaded_file_id': uploaded_file_id,
                'processing_job_id': job.pk,
            }

        mark_job_started(job)
        uploaded_file.status = UploadedFile.Status.PROCESSING
        uploaded_file.validation_errors = []
        uploaded_file.save(
            update_fields=('status', 'validation_errors', 'updated_at')
        )

    try:
        validate_and_profile(uploaded_file, defer_large_files=False)
        mark_job_completed(job)
    except Exception:
        logger.exception('Dataset profiling failed for upload %s', uploaded_file_id)
        uploaded_file.status = UploadedFile.Status.FAILED
        uploaded_file.validation_errors = [
            'Le traitement a échoué en raison d’une erreur interne.'
        ]
        uploaded_file.validated_at = timezone.now()
        uploaded_file.save(
            update_fields=(
                'status',
                'validation_errors',
                'validated_at',
                'updated_at',
            )
        )
        mark_job_failed(job)
        raise

    return {
        'status': uploaded_file.status,
        'uploaded_file_id': uploaded_file_id,
        'processing_job_id': job.pk,
    }


def process_or_enqueue(uploaded_file):
    job = get_or_create_profile_job(uploaded_file)
    synchronous_limit = settings.SYNC_PROFILE_MAX_MB * 1024 * 1024

    if uploaded_file.size <= synchronous_limit:
        mark_job_started(job)
        try:
            validate_and_profile(uploaded_file, defer_large_files=False)
            mark_job_completed(job)
        except Exception:
            mark_job_failed(job)
            raise
        return uploaded_file

    validate_and_profile(uploaded_file)

    def enqueue_after_commit():
        try:
            result = profile_uploaded_file.delay(uploaded_file.pk, job.pk)
            ProcessingJob.objects.filter(pk=job.pk).update(
                celery_task_id=result.id,
                error_message='',
            )
        except Exception:
            logger.exception(
                'Could not enqueue profiling for upload %s',
                uploaded_file.pk,
            )
            ProcessingJob.objects.filter(pk=job.pk).update(
                error_message='Redis est indisponible. La tâche reste en attente.'
            )

    transaction.on_commit(enqueue_after_commit)
    return uploaded_file
