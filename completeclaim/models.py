from django.db import models
from django.contrib.auth.models import User


class CompleteClaim(models.Model):
    casenum = models.CharField(max_length=8)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="complete_tech")

    # The lead that is actively reviewing the case. If null, then no lead is actively reviewing 
    lead_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="complete_lead", null=True)

    claim_time = models.DateTimeField()
    complete_time = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"ID: {self.pk}, Casenum: {self.casenum}, User: {self.user_id.email}, Lead: {self.lead_id.email}, Claim Time: {self.claim_time}, Complete Time: {self.complete_time}"
