from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from apps.datasets.models import UploadedFile
from apps.processing.models import ProcessingJob
from apps.projects.models import Project

from .forms import LoginForm, RegisterForm


@login_required
def home(request):
    uploads = UploadedFile.objects.filter(owner=request.user)
    recent_jobs = ProcessingJob.objects.filter(owner=request.user).select_related(
        'project',
        'uploaded_file',
    )[:5]
    context = {
        'project_count': Project.objects.filter(owner=request.user).count(),
        'upload_count': uploads.count(),
        'validated_count': uploads.filter(status=UploadedFile.Status.VALIDATED).count(),
        'active_job_count': ProcessingJob.objects.filter(
            owner=request.user,
            status__in=(ProcessingJob.Status.PENDING, ProcessingJob.Status.PROCESSING),
        ).count(),
        'recent_jobs': recent_jobs,
    }
    return render(request, 'accounts/home.html', context)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def sign_in(request):
    next_url = request.POST.get('next') or request.GET.get('next')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            return redirect('accounts:home')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


@login_required
def sign_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('accounts:login')

    return render(request, 'accounts/logout.html')
