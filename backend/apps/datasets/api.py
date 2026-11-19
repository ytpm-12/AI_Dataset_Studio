from django.conf import settings
from django.http import HttpResponse
from rest_framework import mixins, parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.ai_engine.models import AIRecommendation
from apps.ai_engine.serializers import AIRecommendationSerializer
from apps.ai_engine.services import (
    AIServiceUnavailable,
    InvalidAIResponse,
    generate_recommendation,
)
from apps.pipelines.models import Transformation
from apps.pipelines.serializers import TransformationSerializer
from apps.pipelines.services import (
    DatasetTooLargeForSynchronousCleaning,
    apply_exact_duplicate_removal,
    apply_missing_value_treatment,
    apply_type_conversion,
    preview_exact_duplicates,
    preview_missing_values,
    TARGET_TYPES,
    build_export,
    build_quality_report,
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

    @action(detail=True, methods=('get',), parser_classes=(), url_path='missing-values/preview')
    def missing_values_preview(self, request, pk=None):
        uploaded_file = self.get_object()
        if uploaded_file.status != UploadedFile.Status.VALIDATED:
            return Response(
                {'detail': "L'analyse est disponible uniquement après validation."},
                status=status.HTTP_409_CONFLICT,
            )
        try:
            result = preview_missing_values(
                uploaded_file,
                max_rows=settings.CLEANING_ANALYSIS_MAX_ROWS,
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise ValidationError({'detail': "Impossible d'analyser les valeurs manquantes."}) from exc
        return Response(result)

    @action(
        detail=True,
        methods=('post',),
        parser_classes=(parsers.JSONParser,),
        url_path='missing-values/apply',
    )
    def missing_values_apply(self, request, pk=None):
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
            transformation = apply_missing_value_treatment(
                uploaded_file,
                max_rows=settings.CLEANING_ANALYSIS_MAX_ROWS,
                column=request.data.get('column'),
                strategy=request.data.get('strategy'),
                value=request.data.get('value'),
            )
        except DatasetTooLargeForSynchronousCleaning as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_409_CONFLICT)
        except (KeyError, ValueError, TypeError) as exc:
            raise ValidationError({'detail': str(exc)}) from exc
        return Response(
            TransformationSerializer(transformation).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=('get',), parser_classes=(), url_path='type-conversion/preview')
    def type_conversion_preview(self, request, pk=None):
        uploaded_file = self.get_object()
        if uploaded_file.status != UploadedFile.Status.VALIDATED:
            return Response(
                {'detail': "L'analyse est disponible uniquement après validation."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            {
                'columns': [
                    {'name': item['name'], 'current_type': item['dtype']}
                    for item in uploaded_file.profile.get('columns', [])
                ],
                'target_types': sorted(TARGET_TYPES),
            }
        )

    @action(
        detail=True,
        methods=('post',),
        parser_classes=(parsers.JSONParser,),
        url_path='type-conversion/apply',
    )
    def type_conversion_apply(self, request, pk=None):
        uploaded_file = self.get_object()
        if request.data.get('confirm') is not True:
            raise ValidationError(
                {'confirm': 'Une confirmation explicite avec la valeur true est obligatoire.'}
            )
        if uploaded_file.status != UploadedFile.Status.VALIDATED:
            return Response(
                {'detail': "La conversion est disponible uniquement après validation."},
                status=status.HTTP_409_CONFLICT,
            )
        if uploaded_file.project_id is None:
            return Response(
                {'detail': 'Le dataset doit appartenir à un projet avant sa conversion.'},
                status=status.HTTP_409_CONFLICT,
            )
        try:
            transformation = apply_type_conversion(
                uploaded_file,
                max_rows=settings.CLEANING_ANALYSIS_MAX_ROWS,
                column=request.data.get('column'),
                target_type=request.data.get('target_type'),
            )
        except DatasetTooLargeForSynchronousCleaning as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_409_CONFLICT)
        except (KeyError, ValueError, TypeError) as exc:
            raise ValidationError({'detail': str(exc)}) from exc
        return Response(
            TransformationSerializer(transformation).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=('get',), parser_classes=(), url_path='export')
    def export(self, request, pk=None):
        uploaded_file = self.get_object()
        if uploaded_file.status != UploadedFile.Status.VALIDATED:
            return Response(
                {'detail': "L'export est disponible uniquement après validation."},
                status=status.HTTP_409_CONFLICT,
            )
        target_format = request.query_params.get('type', 'csv').lower()
        try:
            content, content_type = build_export(
                uploaded_file,
                target_format,
                settings.CLEANING_ANALYSIS_MAX_ROWS,
            )
        except DatasetTooLargeForSynchronousCleaning as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_409_CONFLICT)
        except (KeyError, ValueError, TypeError) as exc:
            raise ValidationError({'detail': str(exc)}) from exc
        filename = f'{uploaded_file.name}.{target_format}'
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(detail=True, methods=('get',), parser_classes=(), url_path='quality-report')
    def quality_report(self, request, pk=None):
        uploaded_file = self.get_object()
        if uploaded_file.status != UploadedFile.Status.VALIDATED:
            return Response(
                {'detail': 'Le rapport est disponible uniquement après validation.'},
                status=status.HTTP_409_CONFLICT,
            )
        try:
            report = build_quality_report(
                uploaded_file,
                settings.CLEANING_ANALYSIS_MAX_ROWS,
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise ValidationError({'detail': 'Impossible de générer le rapport qualité.'}) from exc
        return Response(report)

    @action(
        detail=True,
        methods=('post',),
        parser_classes=(parsers.JSONParser,),
        url_path='ai-recommendations',
    )
    def create_ai_recommendation(self, request, pk=None):
        uploaded_file = self.get_object()
        if uploaded_file.status != UploadedFile.Status.VALIDATED:
            return Response(
                {'detail': "La recommandation est disponible uniquement après validation."},
                status=status.HTTP_409_CONFLICT,
            )
        force_ai = request.data.get('force_ai', False)
        if not isinstance(force_ai, bool):
            raise ValidationError({'force_ai': 'Ce champ doit être booléen.'})
        try:
            recommendation = generate_recommendation(uploaded_file, force_ai=force_ai)
        except AIServiceUnavailable as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except InvalidAIResponse as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        except (KeyError, ValueError, TypeError) as exc:
            raise ValidationError({'detail': str(exc)}) from exc
        return Response(
            AIRecommendationSerializer(recommendation).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=('get',),
        parser_classes=(),
        url_path='ai-recommendations/history',
    )
    def ai_recommendation_history(self, request, pk=None):
        uploaded_file = self.get_object()
        history = AIRecommendation.objects.filter(
            owner=request.user,
            uploaded_file=uploaded_file,
        )
        return Response(AIRecommendationSerializer(history, many=True).data)
