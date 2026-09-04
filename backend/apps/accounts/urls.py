from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.sign_in, name='login'),
    path('auth/logout/', views.sign_out, name='logout'),
]
