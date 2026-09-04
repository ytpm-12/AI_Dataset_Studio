from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import redirect, render

from .forms import UploadedFileForm, compute_sha256, detect_file_type
from .models import UploadedFile


@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES)
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
            messages.success(request, 'Fichier importé. La validation de structure pourra démarrer.')
            return redirect('datasets:upload')
    else:
        form = UploadedFileForm()

    uploads = UploadedFile.objects.filter(owner=request.user)[:10]
    return render(
        request,
        'datasets/upload.html',
        {
            'form': form,
            'uploads': uploads,
            'max_upload_size_mb': settings.MAX_UPLOAD_SIZE_MB,
        },
    )
