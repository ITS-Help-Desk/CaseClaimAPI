from django.db import models
from django.contrib.auth.models import User


class ReviewedClaim(models.Model):
    casenum = models.CharField(max_length=8)
    tech_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="review_tech")
    lead_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="review_lead")

    claim_time = models.DateTimeField()
    complete_time = models.DateTimeField()
    review_time = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=255, choices=[
        ('checked', 'Checked'),
        ('done', 'Done'),
        ('pingedlow', 'Pinged - Low'),
        ('pingedmed', 'Pinged - Medium'),
        ('pingedhigh', 'Pinged - High'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('kudos', 'Kudos'),
    ])

    comment = models.TextField()
    
    # Acknowledgment field (for ping workflow - optional comment when acknowledging)
    acknowledge_comment = models.TextField(blank=True, default='')


    def __str__(self):
        return f"ID: {self.pk}, Casenum: {self.casenum}, Tech: {self.tech_id.email}, Lead: {self.lead_id.email}, Claim Time: {self.claim_time}, Complete Time: {self.complete_time}, Review Time: {self.review_time}, Status: {self.status}, Comment: {self.comment}"
