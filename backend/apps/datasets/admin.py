from django.contrib import admin

from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'file_type', 'status', 'size', 'created_at')
    list_filter = ('file_type', 'status', 'created_at')
    search_fields = ('name', 'original_name', 'checksum_sha256', 'owner__username')
    readonly_fields = (
        'original_name',
        'file_type',
        'content_type',
        'size',
        'checksum_sha256',
        'created_at',
        'updated_at',
    )
