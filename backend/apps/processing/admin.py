from django.contrib import admin

from .models import ProcessingJob


@admin.register(ProcessingJob)
class ProcessingJobAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'kind',
        'status',
        'progress',
        'uploaded_file',
        'owner',
        'attempts',
        'created_at',
    )
    list_filter = ('kind', 'status', 'created_at')
    search_fields = (
        'celery_task_id',
        'uploaded_file__name',
        'project__name',
        'owner__username',
    )
    readonly_fields = (
        'celery_task_id',
        'attempts',
        'started_at',
        'finished_at',
        'created_at',
        'updated_at',
    )
