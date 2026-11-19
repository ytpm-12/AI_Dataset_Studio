from django.contrib import admin

from .models import AIRecommendation


@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ('uploaded_file', 'engine', 'model_name', 'owner', 'created_at')
    list_filter = ('engine', 'created_at')
    search_fields = ('uploaded_file__name', 'owner__username', 'model_name')
    readonly_fields = ('profile_snapshot', 'recommendation', 'created_at')
