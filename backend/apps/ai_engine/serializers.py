from rest_framework import serializers

from .models import AIRecommendation


class AIRecommendationSerializer(serializers.ModelSerializer):
    engine_label = serializers.CharField(source='get_engine_display', read_only=True)

    class Meta:
        model = AIRecommendation
        fields = (
            'id', 'uploaded_file', 'engine', 'engine_label', 'model_name',
            'recommendation', 'created_at',
        )
        read_only_fields = fields
