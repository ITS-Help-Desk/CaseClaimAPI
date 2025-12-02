from django.contrib import admin
from .models import Evaluation


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['tech', 'evaluator', 'period_start', 'period_end', 'overall_rating', 'created_at']
    list_filter = ['overall_rating', 'evaluator', 'created_at']
    search_fields = ['tech__username', 'evaluator__username', 'strengths', 'areas_for_improvement']
    date_hierarchy = 'created_at'

