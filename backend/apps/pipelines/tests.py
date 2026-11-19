from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.datasets.models import UploadedFile
from apps.pipelines.models import Transformation
from apps.projects.models import Project


class DuplicatePreviewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='duplicate-owner',
            password='test-password-123',
        )
        self.other_user = get_user_model().objects.create_user(
            username='other-duplicate-owner',
            password='test-password-123',
        )
        self.project = Project.objects.create(owner=self.user, name='Nettoyage')

    def create_upload(
        self,
        content,
        filename='duplicates.csv',
        file_type=UploadedFile.FileType.CSV,
        content_type='text/csv',
        upload_status=UploadedFile.Status.VALIDATED,
    ):
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
            status=upload_status,
        )
        self.addCleanup(uploaded_file.file.delete, save=False)
        return uploaded_file

    def test_exact_duplicate_preview_counts_removable_rows(self):
        uploaded_file = self.create_upload(
            b'id,name\n1,A\n1,A\n2,B\n2,B\n2,B\n3,C\n'
        )
        self.client.force_authenticate(self.user)

        response = self.client.get(
            f'/api/v1/uploads/{uploaded_file.pk}/duplicates/preview/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['analyzed_rows'], 6)
        self.assertEqual(response.data['affected_rows'], 5)
        self.assertEqual(response.data['duplicate_rows'], 3)
        self.assertEqual(response.data['rows_after_cleanup'], 3)
        self.assertEqual(response.data['duplicate_percentage'], 50.0)
        self.assertEqual(response.data['sample_rows'][0]['_row_number'], 1)
        self.assertFalse(response.data['truncated'])

    def test_json_lists_can_be_compared(self):
        uploaded_file = self.create_upload(
            b'[{"name":"A","tags":[1,2]},{"name":"A","tags":[1,2]}]',
            filename='duplicates.json',
            file_type=UploadedFile.FileType.JSON,
            content_type='application/json',
        )
        self.client.force_authenticate(self.user)

        response = self.client.get(
            f'/api/v1/uploads/{uploaded_file.pk}/duplicates/preview/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['duplicate_rows'], 1)
        self.assertEqual(response.data['affected_rows'], 2)

    @override_settings(CLEANING_ANALYSIS_MAX_ROWS=3)
    def test_analysis_is_bounded_and_reports_truncation(self):
        uploaded_file = self.create_upload(
            b'id,name\n1,A\n1,A\n2,B\n2,B\n'
        )
        self.client.force_authenticate(self.user)

        response = self.client.get(
            f'/api/v1/uploads/{uploaded_file.pk}/duplicates/preview/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['analyzed_rows'], 3)
        self.assertTrue(response.data['truncated'])

    def test_unvalidated_upload_cannot_be_analyzed(self):
        uploaded_file = self.create_upload(
            b'id,name\n1,A\n1,A\n',
            upload_status=UploadedFile.Status.PROCESSING,
        )
        self.client.force_authenticate(self.user)

        response = self.client.get(
            f'/api/v1/uploads/{uploaded_file.pk}/duplicates/preview/'
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_user_cannot_analyze_another_users_upload(self):
        uploaded_file = self.create_upload(b'id,name\n1,A\n1,A\n')
        self.client.force_authenticate(self.other_user)

        response = self.client.get(
            f'/api/v1/uploads/{uploaded_file.pk}/duplicates/preview/'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_apply_duplicate_removal_creates_new_file_and_preserves_source(self):
        uploaded_file = self.create_upload(
            b'id,name\n1,A\n1,A\n2,B\n2,B\n3,C\n'
        )
        source_name = uploaded_file.file.name
        self.client.force_authenticate(self.user)

        response = self.client.post(
            f'/api/v1/uploads/{uploaded_file.pk}/duplicates/apply/',
            {'confirm': True},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], Transformation.Status.COMPLETED)
        self.assertEqual(response.data['summary']['removed_rows'], 2)
        self.assertEqual(response.data['summary']['output_rows'], 3)
        output = UploadedFile.objects.get(pk=response.data['output_file'])
        self.addCleanup(output.file.delete, save=False)
        self.assertEqual(output.status, UploadedFile.Status.VALIDATED)
        self.assertEqual(output.project, uploaded_file.project)
        self.assertNotEqual(output.file.name, source_name)
        self.assertTrue(uploaded_file.file.storage.exists(source_name))
        output.file.open('rb')
        try:
            output_rows = output.file.read().decode('utf-8-sig').splitlines()
            self.assertEqual(output_rows, ['id,name', '1,A', '2,B', '3,C'])
        finally:
            output.file.close()

    def test_apply_requires_explicit_confirmation(self):
        uploaded_file = self.create_upload(b'id\n1\n1\n')
        self.client.force_authenticate(self.user)

        response = self.client.post(
            f'/api/v1/uploads/{uploaded_file.pk}/duplicates/apply/',
            {},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Transformation.objects.exists())

    @override_settings(CLEANING_ANALYSIS_MAX_ROWS=2)
    def test_apply_refuses_partial_cleaning_when_file_is_truncated(self):
        uploaded_file = self.create_upload(b'id\n1\n1\n2\n')
        self.client.force_authenticate(self.user)

        response = self.client.post(
            f'/api/v1/uploads/{uploaded_file.pk}/duplicates/apply/',
            {'confirm': True},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        transformation = Transformation.objects.get(source_file=uploaded_file)
        self.assertEqual(transformation.status, Transformation.Status.FAILED)
        self.assertIsNone(transformation.output_file)

    def test_transformation_history_is_scoped_to_source_and_owner(self):
        uploaded_file = self.create_upload(b'id\n1\n1\n')
        other_upload = self.create_upload(b'id\n2\n2\n', filename='other.csv')
        Transformation.objects.create(
            owner=self.user,
            project=self.project,
            source_file=uploaded_file,
            operation=Transformation.Operation.REMOVE_EXACT_DUPLICATES,
            status=Transformation.Status.COMPLETED,
        )
        Transformation.objects.create(
            owner=self.user,
            project=self.project,
            source_file=other_upload,
            operation=Transformation.Operation.REMOVE_EXACT_DUPLICATES,
            status=Transformation.Status.COMPLETED,
        )
        self.client.force_authenticate(self.user)

        response = self.client.get(
            f'/api/v1/uploads/{uploaded_file.pk}/transformations/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['source_file'], uploaded_file.pk)
