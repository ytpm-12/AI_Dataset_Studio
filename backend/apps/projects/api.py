from django.db.models import Count
from rest_framework import mixins, viewsets

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return (
            Project.objects.filter(owner=self.request.user)
            .annotate(uploaded_file_count=Count('uploaded_files'))
            .order_by('-created_at', '-id')
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
