from django.db import models


class ReviewedClaim(models.Model):
    casenum = models.CharField(max_length=8)
    tech = models.CharField(max_length=256)
    lead = models.CharField(max_length=256)

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
        return f"ID: {self.pk}, Casenum: {self.casenum}, Tech: {self.tech}, Lead: {self.lead}, Claim Time: {self.claim_time}, Complete Time: {self.complete_time}, Review Time: {self.review_time}, Status: {self.status}, Comment: {self.comment}"
