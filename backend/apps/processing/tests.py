from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APITestCase

from apps.datasets.models import UploadedFile
from apps.projects.models import Project

from .models import ProcessingJob


class ProcessingJobModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='job-owner',
            password='test-password-123',
        )
        self.project = Project.objects.create(owner=self.user, name='Job project')
        source = SimpleUploadedFile('job.csv', b'a,b\n1,2\n', content_type='text/csv')
        self.uploaded_file = UploadedFile.objects.create(
            owner=self.user,
            project=self.project,
            name='Job dataset',
            file=source,
            original_name=source.name,
            file_type=UploadedFile.FileType.CSV,
            content_type='text/csv',
            size=source.size,
        )
        self.addCleanup(self.uploaded_file.file.delete, save=False)

    def create_job(self, **overrides):
        values = {
            'owner': self.user,
            'project': self.project,
            'uploaded_file': self.uploaded_file,
            'kind': ProcessingJob.Kind.PROFILE,
        }
        values.update(overrides)
        return ProcessingJob.objects.create(**values)

    def test_job_tracks_dataset_context(self):
        job = self.create_job()

        self.assertEqual(job.owner, self.user)
        self.assertEqual(job.project, self.project)
        self.assertEqual(job.uploaded_file, self.uploaded_file)
        self.assertEqual(job.status, ProcessingJob.Status.PENDING)
        self.assertEqual(job.progress, 0)

    def test_progress_must_be_between_zero_and_one_hundred(self):
        job = ProcessingJob(
            owner=self.user,
            project=self.project,
            uploaded_file=self.uploaded_file,
            kind=ProcessingJob.Kind.PROFILE,
            progress=101,
        )

        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_only_one_active_profile_job_is_allowed(self):
        self.create_job()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_job()

    def test_new_job_is_allowed_after_completion(self):
        self.create_job(
            status=ProcessingJob.Status.COMPLETED,
            progress=100,
        )

        new_job = self.create_job()

        self.assertEqual(new_job.status, ProcessingJob.Status.PENDING)


class ProcessingJobApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='api-job-owner',
            password='test-password-123',
        )
        self.other_user = user_model.objects.create_user(
            username='other-job-owner',
            password='test-password-123',
        )
        self.project = Project.objects.create(owner=self.user, name='API project')
        source = SimpleUploadedFile('api-job.csv', b'a,b\n1,2\n', content_type='text/csv')
        self.uploaded_file = UploadedFile.objects.create(
            owner=self.user,
            project=self.project,
            name='API dataset',
            file=source,
            original_name=source.name,
            file_type=UploadedFile.FileType.CSV,
            content_type='text/csv',
            size=source.size,
        )
        self.addCleanup(self.uploaded_file.file.delete, save=False)
        self.job = ProcessingJob.objects.create(
            owner=self.user,
            project=self.project,
            uploaded_file=self.uploaded_file,
            kind=ProcessingJob.Kind.PROFILE,
        )

    def test_job_list_requires_authentication(self):
        response = self.client.get('/api/v1/jobs/')

        self.assertEqual(response.status_code, 403)

    def test_job_list_returns_only_current_user_jobs(self):
        self.client.force_authenticate(self.user)

        response = self.client.get('/api/v1/jobs/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.job.id)

    def test_job_list_can_be_filtered_by_status(self):
        self.client.force_authenticate(self.user)

        response = self.client.get('/api/v1/jobs/?status=completed')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_job_list_rejects_invalid_filter(self):
        self.client.force_authenticate(self.user)

        response = self.client.get('/api/v1/jobs/?project=not-an-id')

        self.assertEqual(response.status_code, 400)
        self.assertIn('project', response.data)

    def test_other_user_cannot_read_job(self):
        self.client.force_authenticate(self.other_user)

        response = self.client.get(f'/api/v1/jobs/{self.job.id}/')

        self.assertEqual(response.status_code, 404)
