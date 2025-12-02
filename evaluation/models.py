from django.db import models
from django.contrib.auth.models import User


class Evaluation(models.Model):
    """
    Model for storing tech evaluations created by Leads.
    """
    # The tech being evaluated
    tech = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='evaluations_received'
    )
    
    # The lead who created the evaluation
    evaluator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='evaluations_given'
    )
    
    # Evaluation period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Metrics
    cases_reviewed = models.IntegerField(default=0)
    quality_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    ping_count = models.IntegerField(default=0)
    kudos_count = models.IntegerField(default=0)
    
    # Feedback
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    additional_comments = models.TextField(blank=True)
    
    # Overall rating (1-5)
    overall_rating = models.IntegerField(choices=[
        (1, 'Needs Improvement'),
        (2, 'Below Expectations'),
        (3, 'Meets Expectations'),
        (4, 'Exceeds Expectations'),
        (5, 'Outstanding'),
    ], null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Evaluation for {self.tech.username} by {self.evaluator.username} ({self.period_start} - {self.period_end})"

