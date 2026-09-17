from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.api import CsrfTokenView, CurrentUserView, LoginView, LogoutView, RegisterView
from apps.datasets.api import UploadedFileViewSet
from apps.projects.api import ProjectViewSet

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('uploads', UploadedFileViewSet, basename='upload')

urlpatterns = [
    path('auth/csrf/', CsrfTokenView.as_view(), name='api-csrf'),
    path('auth/register/', RegisterView.as_view(), name='api-register'),
    path('auth/login/', LoginView.as_view(), name='api-login'),
    path('auth/me/', CurrentUserView.as_view(), name='api-current-user'),
    path('auth/logout/', LogoutView.as_view(), name='api-logout'),
    path('', include(router.urls)),
]
