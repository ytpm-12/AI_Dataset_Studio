from django.contrib import admin

from .models import Transformation


@admin.register(Transformation)
class TransformationAdmin(admin.ModelAdmin):
    list_display = ('operation', 'source_file', 'output_file', 'status', 'owner', 'created_at')
    list_filter = ('operation', 'status', 'created_at')
    search_fields = ('source_file__name', 'output_file__name', 'owner__username')
    readonly_fields = ('created_at', 'completed_at')
