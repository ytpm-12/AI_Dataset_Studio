from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    uploaded_file_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = (
            'id',
            'name',
            'description',
            'uploaded_file_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'uploaded_file_count', 'created_at', 'updated_at')

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Le nom du projet est obligatoire.')
        return value
