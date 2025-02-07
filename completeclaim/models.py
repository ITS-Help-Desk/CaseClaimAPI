from django.db import models
from django.contrib.auth.models import User


class CompleteClaim(models.Model):
    casenum = models.CharField(max_length=8)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    claim_time = models.DateTimeField()
    complete_time = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"ID: {self.pk}, Casenum: {self.casenum}, User: {self.user.email}, Claim Time: {self.claim_time}, Complete Time: {self.complete_time}"
