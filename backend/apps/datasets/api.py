from rest_framework import mixins, parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import UploadedFile
from .preview import build_dataset_preview
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

    @action(detail=True, methods=('get',), parser_classes=())
    def preview(self, request, pk=None):
        uploaded_file = self.get_object()
        raw_limit = request.query_params.get('limit', '20')
        if not raw_limit.isdecimal():
            raise ValidationError({'limit': 'La limite doit être un entier positif.'})

        limit = int(raw_limit)
        if not 1 <= limit <= 100:
            raise ValidationError({'limit': 'La limite doit être comprise entre 1 et 100.'})
        if uploaded_file.status != UploadedFile.Status.VALIDATED:
            return Response(
                {'detail': "L'aperçu est disponible uniquement après validation."},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            preview = build_dataset_preview(uploaded_file, limit)
        except (KeyError, ValueError, TypeError) as exc:
            raise ValidationError({'detail': "Impossible de générer l'aperçu."}) from exc
        return Response(preview)
