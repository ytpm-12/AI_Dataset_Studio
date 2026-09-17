from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProjectForm
from .models import Project


@login_required
def project_list(request):
    projects = Project.objects.filter(owner=request.user).prefetch_related('uploaded_files')
    return render(request, 'projects/project_list.html', {'projects': projects})


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, f'Le projet « {project.name} » a été créé.')
            return redirect('projects:list')
    else:
        form = ProjectForm()

    return render(request, 'projects/project_form.html', {'form': form})
