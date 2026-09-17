from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class SessionAuthApiTests(TestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.user = get_user_model().objects.create_user(
            username='session-user',
            email='session@example.com',
            password='test-password-123',
        )

    def csrf_token(self):
        response = self.client.get('/api/v1/auth/csrf/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['csrfToken']

    def test_login_requires_csrf_token(self):
        response = self.client.post(
            '/api/v1/auth/login/',
            {'username': self.user.username, 'password': 'test-password-123'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_me_and_logout_flow(self):
        token = self.csrf_token()
        login_response = self.client.post(
            '/api/v1/auth/login/',
            {'username': self.user.username, 'password': 'test-password-123'},
            format='json',
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        me_response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data['username'], self.user.username)

        logout_response = self.client.post(
            '/api/v1/auth/logout/',
            HTTP_X_CSRFTOKEN=self.client.cookies['csrftoken'].value,
        )
        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            self.client.get('/api/v1/auth/me/').status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_registration_creates_and_authenticates_user(self):
        token = self.csrf_token()

        response = self.client.post(
            '/api/v1/auth/register/',
            {
                'username': 'new-api-user',
                'email': 'new-api-user@example.com',
                'password': 'strong-test-password-456',
                'password_confirm': 'strong-test-password-456',
            },
            format='json',
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)
        self.assertTrue(
            get_user_model().objects.filter(username='new-api-user').exists()
        )
        self.assertEqual(
            self.client.get('/api/v1/auth/me/').status_code,
            status.HTTP_200_OK,
        )
