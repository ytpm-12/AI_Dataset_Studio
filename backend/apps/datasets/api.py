from django.conf import settings
from rest_framework import mixins, parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.pipelines.models import Transformation
from apps.pipelines.serializers import TransformationSerializer
from apps.pipelines.services import (
    DatasetTooLargeForSynchronousCleaning,
    apply_exact_duplicate_removal,
    preview_exact_duplicates,
)

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

    @action(
        detail=True,
        methods=('get',),
        parser_classes=(),
        url_path='duplicates/preview',
    )
    def duplicate_preview(self, request, pk=None):
        uploaded_file = self.get_object()
        if uploaded_file.status != UploadedFile.Status.VALIDATED:
            return Response(
                {
                    'detail': (
                        "L'analyse des doublons est disponible uniquement après validation."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        try:
            result = preview_exact_duplicates(
                uploaded_file,
                max_rows=settings.CLEANING_ANALYSIS_MAX_ROWS,
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise ValidationError(
                {'detail': "Impossible d'analyser les doublons."}
            ) from exc
        return Response(result)

    @action(
        detail=True,
        methods=('post',),
        parser_classes=(parsers.JSONParser,),
        url_path='duplicates/apply',
    )
    def duplicate_apply(self, request, pk=None):
        uploaded_file = self.get_object()
        if request.data.get('confirm') is not True:
            raise ValidationError(
                {'confirm': 'Une confirmation explicite avec la valeur true est obligatoire.'}
            )
        if uploaded_file.status != UploadedFile.Status.VALIDATED:
            return Response(
                {'detail': "Le nettoyage est disponible uniquement après validation."},
                status=status.HTTP_409_CONFLICT,
            )
        if uploaded_file.project_id is None:
            return Response(
                {'detail': 'Le dataset doit appartenir à un projet avant son nettoyage.'},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            transformation = apply_exact_duplicate_removal(
                uploaded_file,
                max_rows=settings.CLEANING_ANALYSIS_MAX_ROWS,
            )
        except DatasetTooLargeForSynchronousCleaning as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_409_CONFLICT)
        except (KeyError, ValueError, TypeError) as exc:
            raise ValidationError({'detail': str(exc)}) from exc

        return Response(
            TransformationSerializer(transformation).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=('get',), parser_classes=(), url_path='transformations')
    def transformations(self, request, pk=None):
        uploaded_file = self.get_object()
        history = Transformation.objects.filter(
            owner=request.user,
            source_file=uploaded_file,
        ).select_related('source_file', 'output_file')
        return Response(TransformationSerializer(history, many=True).data)
