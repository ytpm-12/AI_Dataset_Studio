import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from .models import UploadedFile
from .profiling import validate_and_profile


logger = logging.getLogger(__name__)


@shared_task(ignore_result=False)
def profile_uploaded_file(uploaded_file_id):
    with transaction.atomic():
        try:
            uploaded_file = UploadedFile.objects.select_for_update().get(
                pk=uploaded_file_id
            )
        except UploadedFile.DoesNotExist:
            return {'status': 'missing', 'uploaded_file_id': uploaded_file_id}

        if uploaded_file.status in {
            UploadedFile.Status.PROCESSING,
            UploadedFile.Status.VALIDATED,
            UploadedFile.Status.INVALID,
        }:
            return {
                'status': uploaded_file.status,
                'uploaded_file_id': uploaded_file_id,
            }

        uploaded_file.status = UploadedFile.Status.PROCESSING
        uploaded_file.validation_errors = []
        uploaded_file.save(
            update_fields=('status', 'validation_errors', 'updated_at')
        )

    try:
        validate_and_profile(uploaded_file, defer_large_files=False)
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
        raise

    return {
        'status': uploaded_file.status,
        'uploaded_file_id': uploaded_file_id,
    }


def process_or_enqueue(uploaded_file):
    validate_and_profile(uploaded_file)
    if uploaded_file.status == UploadedFile.Status.VALIDATION_PENDING:
        def enqueue_after_commit():
            try:
                profile_uploaded_file.delay(uploaded_file.pk)
            except Exception:
                logger.exception(
                    'Could not enqueue profiling for upload %s',
                    uploaded_file.pk,
                )

        transaction.on_commit(enqueue_after_commit)
    return uploaded_file
