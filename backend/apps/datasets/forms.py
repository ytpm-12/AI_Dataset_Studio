import hashlib
from pathlib import Path

from django import forms
from django.conf import settings

from .models import UploadedFile


FILE_TYPE_BY_EXTENSION = {
    '.csv': UploadedFile.FileType.CSV,
    '.json': UploadedFile.FileType.JSON,
    '.xml': UploadedFile.FileType.XML,
}


def detect_file_type(filename):
    return FILE_TYPE_BY_EXTENSION.get(Path(filename).suffix.lower())


def compute_sha256(uploaded_file):
    current_position = uploaded_file.tell()
    uploaded_file.seek(0)

    digest = hashlib.sha256()
    for chunk in uploaded_file.chunks():
        digest.update(chunk)

    uploaded_file.seek(current_position)
    return digest.hexdigest()


class UploadedFileForm(forms.ModelForm):
    name = forms.CharField(
        label='Nom du dataset',
        required=False,
        max_length=180,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: tickets-support-septembre'}),
    )
    file = forms.FileField(
        label='Fichier source',
        widget=forms.ClearableFileInput(
            attrs={'accept': '.csv,.json,.xml'}
        ),
    )

    class Meta:
        model = UploadedFile
        fields = ('name', 'file')

    def clean_file(self):
        uploaded_file = self.cleaned_data['file']
        extension = Path(uploaded_file.name).suffix.lower()

        if extension not in FILE_TYPE_BY_EXTENSION:
            allowed = ', '.join(sorted(FILE_TYPE_BY_EXTENSION))
            raise forms.ValidationError(f'Format non supporté. Formats acceptés: {allowed}.')

        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if uploaded_file.size > max_size:
            raise forms.ValidationError(
                f'Fichier trop volumineux. Taille maximale: {settings.MAX_UPLOAD_SIZE_MB} Mo.'
            )

        return uploaded_file

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        uploaded_file = self.files.get('file')

        if name:
            return name

        if uploaded_file:
            return Path(uploaded_file.name).stem[:180]

        return name
