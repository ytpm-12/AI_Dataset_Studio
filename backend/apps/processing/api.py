from celery.exceptions import CeleryError
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.datasets.models import UploadedFile
from apps.datasets.tasks import profile_uploaded_file

from .models import ProcessingJob
from .serializers import ProcessingJobSerializer


class ProcessingJobViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProcessingJobSerializer

    def get_queryset(self):
        queryset = ProcessingJob.objects.filter(owner=self.request.user).select_related(
            'project',
            'uploaded_file',
        )

        status = self.request.query_params.get('status')
        project = self.request.query_params.get('project')
        uploaded_file = self.request.query_params.get('upload')

        if status:
            valid_statuses = {choice.value for choice in ProcessingJob.Status}
            if status not in valid_statuses:
                raise ValidationError({'status': 'Statut de traitement invalide.'})
            queryset = queryset.filter(status=status)
        if project:
            if not project.isdecimal():
                raise ValidationError({'project': 'Identifiant de projet invalide.'})
            queryset = queryset.filter(project_id=project)
        if uploaded_file:
            if not uploaded_file.isdecimal():
                raise ValidationError({'upload': 'Identifiant de fichier invalide.'})
            queryset = queryset.filter(uploaded_file_id=uploaded_file)

        return queryset

    @action(detail=True, methods=('post',))
    def retry(self, request, pk=None):
        with transaction.atomic():
            job = get_object_or_404(
                ProcessingJob.objects.filter(owner=request.user).select_for_update(),
                pk=pk,
            )
            if job.status != ProcessingJob.Status.FAILED:
                raise ValidationError(
                    {'status': 'Seul un traitement en échec peut être relancé.'}
                )

            job.status = ProcessingJob.Status.PENDING
            job.progress = 0
            job.celery_task_id = ''
            job.error_message = ''
            job.started_at = None
            job.finished_at = None
            job.save(
                update_fields=(
                    'status',
                    'progress',
                    'celery_task_id',
                    'error_message',
                    'started_at',
                    'finished_at',
                    'updated_at',
                )
            )
            UploadedFile.objects.filter(pk=job.uploaded_file_id).update(
                status=UploadedFile.Status.VALIDATION_PENDING,
                validation_errors=[],
                validated_at=None,
            )

        try:
            result = profile_uploaded_file.delay(job.uploaded_file_id, job.pk)
        except (CeleryError, ConnectionError, OSError) as exc:
            message = 'Redis est indisponible. La tâche reste en attente.'
            ProcessingJob.objects.filter(pk=job.pk).update(error_message=message)
            return Response(
                {'detail': message},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        job.celery_task_id = result.id
        job.save(update_fields=('celery_task_id', 'updated_at'))
        return Response(
            self.get_serializer(job).data,
            status=status.HTTP_202_ACCEPTED,
        )
