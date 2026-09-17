from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project

from .models import UploadedFile


class UploadedFileModelTests(TestCase):
    def test_uploaded_file_can_belong_to_a_project(self):
        user = get_user_model().objects.create_user(
            username='dataset-owner',
            password='test-password-123',
        )
        project = Project.objects.create(owner=user, name='Donnees ventes')
        source = SimpleUploadedFile('ventes.csv', b'product,amount\nA,10\n')

        uploaded_file = UploadedFile.objects.create(
            owner=user,
            project=project,
            name='Ventes',
            file=source,
            original_name=source.name,
            file_type=UploadedFile.FileType.CSV,
            content_type='text/csv',
            size=source.size,
        )

        self.assertEqual(uploaded_file.project, project)
        self.assertEqual(list(project.uploaded_files.all()), [uploaded_file])
        uploaded_file.file.delete(save=False)


class UploadedFileApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='api-dataset-owner',
            password='test-password-123',
        )
        self.other_user = get_user_model().objects.create_user(
            username='other-dataset-owner',
            password='test-password-123',
        )
        self.project = Project.objects.create(owner=self.user, name='Projet API')
        self.other_project = Project.objects.create(
            owner=self.other_user,
            name='Projet privé',
        )

    def test_upload_is_linked_to_authenticated_users_project(self):
        self.client.force_authenticate(self.user)
        source = SimpleUploadedFile(
            'ventes.csv',
            b'product,amount\nA,10\n',
            content_type='text/csv',
        )

        response = self.client.post(
            '/api/v1/uploads/',
            {'project': self.project.pk, 'name': 'Ventes API', 'file': source},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        uploaded_file = UploadedFile.objects.get(pk=response.data['id'])
        self.assertEqual(uploaded_file.owner, self.user)
        self.assertEqual(uploaded_file.project, self.project)
        uploaded_file.file.delete(save=False)

    def test_user_cannot_upload_to_another_users_project(self):
        self.client.force_authenticate(self.user)
        source = SimpleUploadedFile('data.csv', b'a,b\n1,2\n', content_type='text/csv')

        response = self.client.post(
            '/api/v1/uploads/',
            {'project': self.other_project.pk, 'name': 'Interdit', 'file': source},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(UploadedFile.objects.filter(owner=self.user).exists())
