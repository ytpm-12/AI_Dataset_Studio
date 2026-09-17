from rest_framework import mixins, parsers, viewsets

from .models import UploadedFile
from .serializers import UploadedFileSerializer


class UploadedFileViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UploadedFileSerializer
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def get_queryset(self):
        return UploadedFile.objects.filter(owner=self.request.user).select_related('project')
