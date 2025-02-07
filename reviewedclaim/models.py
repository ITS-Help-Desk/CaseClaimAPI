from django.db import models
from django.contrib.auth.models import User


class ReviewedClaim(models.Model):
    casenum = models.CharField(max_length=8)
    tech = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tech")
    lead = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lead")

    claim_time = models.DateTimeField()
    complete_time = models.DateTimeField()
    review_time = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=255, choices=[
        ('checked', 'Checked'),
        ('done', 'Done'),
        ('pingedlow', 'Pinged - Low'),
        ('pingedmed', 'Pinged - Medium'),
        ('pingedhigh', 'Pinged - High'),
        ('resolved', 'Resolved'),
        ('kudos', 'Kudos'),
    ])

    comment = models.TextField()


    def __str__(self):
        return f"ID: {self.pk}, Casenum: {self.casenum}, Tech: {self.tech.email}, Lead: {self.lead.email}, Claim Time: {self.claim_time}, Complete Time: {self.complete_time}, Review Time: {self.review_time}, Status: {self.status}, Comment: {self.comment}"
