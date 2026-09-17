from pathlib import Path

from django.conf import settings
from rest_framework import serializers

from apps.projects.models import Project

from .models import UploadedFile
from .services import FILE_TYPE_BY_EXTENSION, compute_sha256, detect_file_type


class UploadedFileSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.none())

    class Meta:
        model = UploadedFile
        fields = (
            'id',
            'project',
            'name',
            'file',
            'original_name',
            'file_type',
            'content_type',
            'size',
            'checksum_sha256',
            'status',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'original_name',
            'file_type',
            'content_type',
            'size',
            'checksum_sha256',
            'status',
            'created_at',
            'updated_at',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['project'].queryset = Project.objects.filter(owner=request.user)

    def validate_file(self, uploaded_file):
        extension = Path(uploaded_file.name).suffix.lower()
        if extension not in FILE_TYPE_BY_EXTENSION:
            allowed = ', '.join(sorted(FILE_TYPE_BY_EXTENSION))
            raise serializers.ValidationError(
                f'Format non supporté. Formats acceptés: {allowed}.'
            )

        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if uploaded_file.size > max_size:
            raise serializers.ValidationError(
                f'Fichier trop volumineux. Taille maximale: {settings.MAX_UPLOAD_SIZE_MB} Mo.'
            )
        return uploaded_file

    def create(self, validated_data):
        uploaded_file = validated_data['file']
        request = self.context['request']
        name = validated_data.pop('name', '').strip()

        return UploadedFile.objects.create(
            **validated_data,
            owner=request.user,
            name=name or Path(uploaded_file.name).stem[:180],
            original_name=uploaded_file.name,
            file_type=detect_file_type(uploaded_file.name),
            content_type=uploaded_file.content_type or '',
            size=uploaded_file.size,
            checksum_sha256=compute_sha256(uploaded_file),
            status=UploadedFile.Status.UPLOADED,
        )
