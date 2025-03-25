from django.db import models
from django.contrib.auth.models import User


class ActiveClaim(models.Model):
    casenum = models.CharField(max_length=8, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    claim_time = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"ID: {self.pk}, Casenum: {self.casenum}, User ID: {self.user.email}, Claim Time: {self.claim_time}"
