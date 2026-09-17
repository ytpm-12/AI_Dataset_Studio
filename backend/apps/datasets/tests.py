from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project

from .models import UploadedFile
from .profiling import validate_and_profile


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
        self.assertEqual(uploaded_file.status, UploadedFile.Status.VALIDATED)
        self.assertEqual(uploaded_file.profile['column_count'], 2)
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


class DatasetProfilingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='profiling-owner',
            password='test-password-123',
        )
        self.project = Project.objects.create(owner=self.user, name='Profilage')

    def create_upload(self, filename, content, file_type, content_type):
        source = SimpleUploadedFile(filename, content, content_type=content_type)
        uploaded_file = UploadedFile.objects.create(
            owner=self.user,
            project=self.project,
            name=filename,
            file=source,
            original_name=filename,
            file_type=file_type,
            content_type=content_type,
            size=source.size,
        )
        self.addCleanup(uploaded_file.file.delete, save=False)
        return uploaded_file

    def test_csv_profile_contains_column_statistics(self):
        uploaded_file = self.create_upload(
            'clients.csv',
            b'name,age\nAlice,30\nBob,\n',
            UploadedFile.FileType.CSV,
            'text/csv',
        )

        validate_and_profile(uploaded_file)

        self.assertEqual(uploaded_file.status, UploadedFile.Status.VALIDATED)
        self.assertEqual(uploaded_file.profile['rows_profiled'], 2)
        self.assertEqual(uploaded_file.profile['columns'][1]['missing_count'], 1)

    def test_json_and_xml_are_profiled(self):
        json_upload = self.create_upload(
            'clients.json',
            b'[{"name": "Alice", "active": true}]',
            UploadedFile.FileType.JSON,
            'application/json',
        )
        xml_upload = self.create_upload(
            'clients.xml',
            b'<clients><client><name>Alice</name><age>30</age></client></clients>',
            UploadedFile.FileType.XML,
            'application/xml',
        )

        validate_and_profile(json_upload)
        validate_and_profile(xml_upload)

        self.assertEqual(json_upload.status, UploadedFile.Status.VALIDATED)
        self.assertEqual(xml_upload.status, UploadedFile.Status.VALIDATED)
        self.assertEqual(json_upload.profile['column_count'], 2)
        self.assertEqual(xml_upload.profile['column_count'], 2)

    def test_invalid_json_is_recorded_without_server_error(self):
        uploaded_file = self.create_upload(
            'invalid.json',
            b'{not-json}',
            UploadedFile.FileType.JSON,
            'application/json',
        )

        validate_and_profile(uploaded_file)

        self.assertEqual(uploaded_file.status, UploadedFile.Status.INVALID)
        self.assertTrue(uploaded_file.validation_errors)
        self.assertIsNotNone(uploaded_file.validated_at)

    def test_xml_entities_are_rejected(self):
        uploaded_file = self.create_upload(
            'unsafe.xml',
            (
                b'<!DOCTYPE data [<!ENTITY secret SYSTEM "file:///etc/passwd">]>'
                b'<data><row><value>&secret;</value></row></data>'
            ),
            UploadedFile.FileType.XML,
            'application/xml',
        )

        validate_and_profile(uploaded_file)

        self.assertEqual(uploaded_file.status, UploadedFile.Status.INVALID)
        self.assertTrue(uploaded_file.validation_errors)

    @override_settings(SYNC_PROFILE_MAX_MB=0)
    def test_large_file_is_deferred(self):
        uploaded_file = self.create_upload(
            'deferred.csv',
            b'a,b\n1,2\n',
            UploadedFile.FileType.CSV,
            'text/csv',
        )

        validate_and_profile(uploaded_file)

        self.assertEqual(
            uploaded_file.status,
            UploadedFile.Status.VALIDATION_PENDING,
        )
        self.assertTrue(uploaded_file.profile['deferred'])
        self.assertIsNone(uploaded_file.validated_at)
