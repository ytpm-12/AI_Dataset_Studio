from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase

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
