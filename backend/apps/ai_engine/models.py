from django.conf import settings
from django.db import models


class AIRecommendation(models.Model):
    class Engine(models.TextChoices):
        RULES = 'rules', 'Deterministic rules'
        OLLAMA = 'ollama', 'Ollama'
        OPENAI_COMPATIBLE = 'openai_compatible', 'OpenAI-compatible API'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_recommendations',
    )
    uploaded_file = models.ForeignKey(
        'datasets.UploadedFile',
        on_delete=models.CASCADE,
        related_name='ai_recommendations',
    )
    engine = models.CharField(max_length=32, choices=Engine.choices)
    model_name = models.CharField(max_length=180, blank=True)
    profile_snapshot = models.JSONField(default=dict)
    recommendation = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = (
            models.Index(fields=('owner', '-created_at')),
            models.Index(fields=('uploaded_file', '-created_at')),
        )

    def __str__(self):
        return f'{self.uploaded_file} - {self.engine}'
