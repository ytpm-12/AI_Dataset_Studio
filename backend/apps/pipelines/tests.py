import json

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

    def test_missing_values_preview_reports_each_column(self):
        uploaded_file = self.create_upload(b'id,name,score\n1,A,10\n2,,\n3,C,30\n')
        self.client.force_authenticate(self.user)

        response = self.client.get(
            f'/api/v1/uploads/{uploaded_file.pk}/missing-values/preview/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_missing_values'], 2)
        name_column = next(item for item in response.data['columns'] if item['name'] == 'name')
        self.assertEqual(name_column['missing_count'], 1)

    def test_missing_values_can_be_filled_with_constant(self):
        uploaded_file = self.create_upload(b'id,name\n1,A\n2,\n3,C\n')
        self.client.force_authenticate(self.user)

        response = self.client.post(
            f'/api/v1/uploads/{uploaded_file.pk}/missing-values/apply/',
            {'confirm': True, 'column': 'name', 'strategy': 'constant', 'value': 'Inconnu'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['summary']['missing_before'], 1)
        self.assertEqual(response.data['summary']['missing_after'], 0)
        output = UploadedFile.objects.get(pk=response.data['output_file'])
        self.addCleanup(output.file.delete, save=False)
        output.file.open('rb')
        try:
            self.assertIn('2,Inconnu', output.file.read().decode('utf-8-sig'))
        finally:
            output.file.close()

    def test_missing_values_can_be_filled_with_numeric_mean(self):
        uploaded_file = self.create_upload(b'id,score\n1,10\n2,\n3,30\n')
        self.client.force_authenticate(self.user)

        response = self.client.post(
            f'/api/v1/uploads/{uploaded_file.pk}/missing-values/apply/',
            {'confirm': True, 'column': 'score', 'strategy': 'mean'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        output = UploadedFile.objects.get(pk=response.data['output_file'])
        self.addCleanup(output.file.delete, save=False)
        self.assertEqual(response.data['summary']['missing_after'], 0)

    def test_missing_values_drop_rows_reports_removed_rows(self):
        uploaded_file = self.create_upload(b'id,name\n1,A\n2,\n3,C\n')
        self.client.force_authenticate(self.user)

        response = self.client.post(
            f'/api/v1/uploads/{uploaded_file.pk}/missing-values/apply/',
            {'confirm': True, 'column': 'name', 'strategy': 'drop_rows'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['summary']['removed_rows'], 1)
        output = UploadedFile.objects.get(pk=response.data['output_file'])
        self.addCleanup(output.file.delete, save=False)

    def test_mean_is_rejected_for_text_column(self):
        uploaded_file = self.create_upload(b'id,name\n1,A\n2,\n3,C\n')
        self.client.force_authenticate(self.user)

        response = self.client.post(
            f'/api/v1/uploads/{uploaded_file.pk}/missing-values/apply/',
            {'confirm': True, 'column': 'name', 'strategy': 'mean'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        transformation = Transformation.objects.get(source_file=uploaded_file)
        self.assertEqual(transformation.status, Transformation.Status.FAILED)

    def test_type_conversion_preview_lists_columns_and_targets(self):
        uploaded_file = self.create_upload(b'id,active\n1,yes\n2,no\n')
        uploaded_file.profile = {
            'columns': [
                {'name': 'id', 'dtype': 'int64'},
                {'name': 'active', 'dtype': 'object'},
            ]
        }
        uploaded_file.save(update_fields=('profile', 'updated_at'))
        self.client.force_authenticate(self.user)

        response = self.client.get(
            f'/api/v1/uploads/{uploaded_file.pk}/type-conversion/preview/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('boolean', response.data['target_types'])
        self.assertEqual(response.data['columns'][1]['name'], 'active')

    def test_text_values_can_be_converted_to_boolean(self):
        uploaded_file = self.create_upload(b'id,active\n1,yes\n2,no\n3,oui\n')
        self.client.force_authenticate(self.user)

        response = self.client.post(
            f'/api/v1/uploads/{uploaded_file.pk}/type-conversion/apply/',
            {'confirm': True, 'column': 'active', 'target_type': 'boolean'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['summary']['target_type'], 'boolean')
        output = UploadedFile.objects.get(pk=response.data['output_file'])
        self.addCleanup(output.file.delete, save=False)

    def test_decimal_values_cannot_be_silently_converted_to_integer(self):
        uploaded_file = self.create_upload(b'id,score\n1,10.5\n2,20\n')
        self.client.force_authenticate(self.user)

        response = self.client.post(
            f'/api/v1/uploads/{uploaded_file.pk}/type-conversion/apply/',
            {'confirm': True, 'column': 'score', 'target_type': 'integer'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('décimales', response.data['detail'])

    def test_invalid_boolean_value_is_rejected(self):
        uploaded_file = self.create_upload(b'id,active\n1,maybe\n2,yes\n')
        self.client.force_authenticate(self.user)

        response = self.client.post(
            f'/api/v1/uploads/{uploaded_file.pk}/type-conversion/apply/',
            {'confirm': True, 'column': 'active', 'target_type': 'boolean'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dataset_can_be_exported_as_json(self):
        uploaded_file = self.create_upload(b'id,name\n1,A\n2,B\n')
        self.client.force_authenticate(self.user)

        response = self.client.get(
            f'/api/v1/uploads/{uploaded_file.pk}/export/?type=json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertEqual(json.loads(response.content)[0]['name'], 'A')

    def test_invalid_export_format_is_rejected(self):
        uploaded_file = self.create_upload(b'id\n1\n')
        self.client.force_authenticate(self.user)

        response = self.client.get(
            f'/api/v1/uploads/{uploaded_file.pk}/export/?type=xlsx'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_quality_report_scores_missing_and_duplicate_rows(self):
        uploaded_file = self.create_upload(b'id,name\n1,A\n1,A\n2,\n')
        self.client.force_authenticate(self.user)

        response = self.client.get(
            f'/api/v1/uploads/{uploaded_file.pk}/quality-report/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['missing_values'], 1)
        self.assertEqual(response.data['duplicate_rows'], 1)
        self.assertLess(response.data['overall_score'], 100)
