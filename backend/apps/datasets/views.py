from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import redirect, render

from .forms import UploadedFileForm
from .models import UploadedFile
from .services import compute_sha256, detect_file_type
from .tasks import process_or_enqueue


@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.original_name = uploaded_file.name
            instance.file_type = detect_file_type(uploaded_file.name)
            instance.content_type = uploaded_file.content_type or ''
            instance.size = uploaded_file.size
            instance.checksum_sha256 = compute_sha256(uploaded_file)
            instance.status = UploadedFile.Status.UPLOADED
            instance.save()
            process_or_enqueue(instance)
            if instance.status == UploadedFile.Status.VALIDATED:
                messages.success(request, 'Fichier importé et validé avec succès.')
            elif instance.status == UploadedFile.Status.INVALID:
                messages.error(request, 'Fichier importé, mais sa structure est invalide.')
            else:
                messages.info(request, 'Fichier importé. Son analyse sera traitée en arrière-plan.')
            return redirect('datasets:upload')
    else:
        form = UploadedFileForm(user=request.user)

    uploads = UploadedFile.objects.filter(owner=request.user).select_related('project')[:10]
    return render(
        request,
        'datasets/upload.html',
        {
            'form': form,
            'has_projects': request.user.projects.exists(),
            'uploads': uploads,
            'max_upload_size_mb': settings.MAX_UPLOAD_SIZE_MB,
        },
    )
