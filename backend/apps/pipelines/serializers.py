from rest_framework import serializers

from .models import Transformation


class TransformationSerializer(serializers.ModelSerializer):
    operation_label = serializers.CharField(source='get_operation_display', read_only=True)

    class Meta:
        model = Transformation
        fields = (
            'id',
            'source_file',
            'output_file',
            'operation',
            'operation_label',
            'status',
            'parameters',
            'summary',
            'error_message',
            'created_at',
            'completed_at',
        )
        read_only_fields = fields
