from django.core.management.base import BaseCommand

from apps.datasets.models import UploadedFile
from apps.datasets.tasks import get_or_create_profile_job, profile_uploaded_file
from apps.processing.models import ProcessingJob


class Command(BaseCommand):
    help = 'Envoie les imports en attente vers la file Celery.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100)

    def handle(self, *args, **options):
        limit = max(1, options['limit'])
        uploads = list(
            UploadedFile.objects.filter(
                status=UploadedFile.Status.VALIDATION_PENDING
            )
            .select_related('owner', 'project')
            .order_by('created_at')
            [:limit]
        )

        enqueued = 0
        for uploaded_file in uploads:
            job = get_or_create_profile_job(uploaded_file)
            result = profile_uploaded_file.delay(uploaded_file.pk, job.pk)
            ProcessingJob.objects.filter(pk=job.pk).update(
                celery_task_id=result.id,
                error_message='',
            )
            enqueued += 1

        self.stdout.write(
            self.style.SUCCESS(f'{enqueued} tâche(s) envoyée(s) à Celery.')
        )
