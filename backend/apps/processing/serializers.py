from rest_framework import serializers

from .models import ProcessingJob


class ProcessingJobSerializer(serializers.ModelSerializer):
    kind_label = serializers.CharField(source='get_kind_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    uploaded_file_name = serializers.CharField(
        source='uploaded_file.original_name',
        read_only=True,
    )

    class Meta:
        model = ProcessingJob
        fields = (
            'id',
            'project',
            'uploaded_file',
            'uploaded_file_name',
            'kind',
            'kind_label',
            'status',
            'status_label',
            'progress',
            'attempts',
            'error_message',
            'started_at',
            'finished_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields
