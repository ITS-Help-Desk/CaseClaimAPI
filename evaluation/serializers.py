from rest_framework import serializers
from .models import Evaluation


class EvaluationSerializer(serializers.ModelSerializer):
    tech_username = serializers.CharField(source='tech.username', read_only=True)
    tech_name = serializers.SerializerMethodField()
    evaluator_username = serializers.CharField(source='evaluator.username', read_only=True)
    evaluator_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Evaluation
        fields = [
            'id',
            'tech',
            'tech_username',
            'tech_name',
            'evaluator',
            'evaluator_username',
            'evaluator_name',
            'period_start',
            'period_end',
            'cases_reviewed',
            'quality_score',
            'ping_count',
            'kudos_count',
            'strengths',
            'areas_for_improvement',
            'additional_comments',
            'overall_rating',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'evaluator', 'created_at', 'updated_at']
    
    def get_tech_name(self, obj):
        return f"{obj.tech.first_name} {obj.tech.last_name}".strip() or obj.tech.username
    
    def get_evaluator_name(self, obj):
        return f"{obj.evaluator.first_name} {obj.evaluator.last_name}".strip() or obj.evaluator.username

