from django.core.management.base import BaseCommand

from apps.datasets.models import UploadedFile
from apps.datasets.tasks import profile_uploaded_file


class Command(BaseCommand):
    help = 'Envoie les imports en attente vers la file Celery.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100)

    def handle(self, *args, **options):
        limit = max(1, options['limit'])
        upload_ids = list(
            UploadedFile.objects.filter(
                status=UploadedFile.Status.VALIDATION_PENDING
            )
            .order_by('created_at')
            .values_list('pk', flat=True)[:limit]
        )

        enqueued = 0
        for uploaded_file_id in upload_ids:
            profile_uploaded_file.delay(uploaded_file_id)
            enqueued += 1

        self.stdout.write(
            self.style.SUCCESS(f'{enqueued} tâche(s) envoyée(s) à Celery.')
        )
