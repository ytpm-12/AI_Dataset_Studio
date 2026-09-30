from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

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
