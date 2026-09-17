from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Project


class ProjectModelTests(TestCase):
    def test_project_belongs_to_its_owner(self):
        user = get_user_model().objects.create_user(
            username='project-owner',
            password='test-password-123',
        )

        project = Project.objects.create(owner=user, name='Qualite clients')

        self.assertEqual(project.owner, user)
        self.assertEqual(str(project), 'Qualite clients')


class ProjectApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='api-project-owner',
            password='test-password-123',
        )
        self.other_user = get_user_model().objects.create_user(
            username='other-project-owner',
            password='test-password-123',
        )
        self.project = Project.objects.create(owner=self.user, name='Projet visible')
        Project.objects.create(owner=self.other_user, name='Projet privé')

    def test_authentication_is_required(self):
        response = self.client.get('/api/v1/projects/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_only_sees_their_projects(self):
        self.client.force_authenticate(self.user)

        response = self.client.get('/api/v1/projects/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Projet visible')

    def test_created_project_uses_authenticated_user_as_owner(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(
            '/api/v1/projects/',
            {'name': 'Nouveau projet', 'description': 'API'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_project = Project.objects.get(pk=response.data['id'])
        self.assertEqual(created_project.owner, self.user)

    def test_user_cannot_retrieve_another_users_project(self):
        private_project = Project.objects.get(owner=self.other_user)
        self.client.force_authenticate(self.user)

        response = self.client.get(f'/api/v1/projects/{private_project.pk}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
