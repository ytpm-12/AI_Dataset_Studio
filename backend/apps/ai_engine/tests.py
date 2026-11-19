from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.datasets.models import UploadedFile
from apps.projects.models import Project

from .models import AIRecommendation
from .services import AIServiceUnavailable, InvalidAIResponse, validate_recommendation


class AIRecommendationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='ai-owner', password='pass-123')
        self.other_user = get_user_model().objects.create_user(username='ai-other', password='pass-123')
        self.project = Project.objects.create(owner=self.user, name='AI project')

    def create_upload(self, content=b'id,name\n1,A\n2,\n'):
        source = SimpleUploadedFile('ai.csv', content, content_type='text/csv')
        upload = UploadedFile.objects.create(
            owner=self.user,
            project=self.project,
            name='AI dataset',
            file=source,
            original_name='ai.csv',
            file_type=UploadedFile.FileType.CSV,
            content_type='text/csv',
            size=source.size,
            status=UploadedFile.Status.VALIDATED,
            profile={
                'rows_profiled': 2,
                'column_count': 2,
                'columns': [
                    {'name': 'id', 'dtype': 'int64', 'missing_count': 0},
                    {'name': 'name', 'dtype': 'object', 'missing_count': 1},
                ],
            },
        )
        self.addCleanup(upload.file.delete, save=False)
        return upload

    def test_hybrid_engine_uses_rules_for_missing_values(self):
        upload = self.create_upload()
        self.client.force_authenticate(self.user)

        response = self.client.post(
            f'/api/v1/uploads/{upload.pk}/ai-recommendations/',
            {'force_ai': False},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['engine'], AIRecommendation.Engine.RULES)
        self.assertEqual(response.data['recommendation']['action'], 'impute_missing')
        self.assertTrue(response.data['recommendation']['requires_validation'])

    @patch('apps.ai_engine.services.request_model_recommendation')
    def test_force_ai_uses_configured_model_service(self, request_model):
        request_model.return_value = (
            {
                'action': 'request_human_review',
                'target': 'dataset',
                'parameters': {},
                'confidence': 0.7,
                'explanation': 'Le profil reste ambigu.',
                'requires_validation': True,
            },
            AIRecommendation.Engine.OLLAMA,
        )
        upload = self.create_upload()
        self.client.force_authenticate(self.user)

        response = self.client.post(
            f'/api/v1/uploads/{upload.pk}/ai-recommendations/',
            {'force_ai': True},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['engine'], AIRecommendation.Engine.OLLAMA)
        request_model.assert_called_once()

    @patch('apps.datasets.api.generate_recommendation')
    def test_unavailable_ai_service_returns_503(self, generate):
        generate.side_effect = AIServiceUnavailable('Service indisponible.')
        upload = self.create_upload(content=b'id,name\n1,A\n2,B\n')
        self.client.force_authenticate(self.user)

        response = self.client.post(
            f'/api/v1/uploads/{upload.pk}/ai-recommendations/',
            {'force_ai': True},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_other_user_cannot_access_ai_history(self):
        upload = self.create_upload()
        self.client.force_authenticate(self.other_user)

        response = self.client.get(
            f'/api/v1/uploads/{upload.pk}/ai-recommendations/history/'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_contract_is_rejected(self):
        with self.assertRaises(InvalidAIResponse):
            validate_recommendation(
                {
                    'action': 'drop_duplicates',
                    'target': 'dataset',
                    'parameters': {},
                    'confidence': 2,
                    'explanation': 'Invalide',
                    'requires_validation': False,
                }
            )
