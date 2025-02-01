from django.db import models


class ActiveClaim(models.Model):
    casenum = models.CharField(max_length=8, unique=True)
    user = models.CharField(max_length=256)

    claim_time = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"ID: {self.pk}, Casenum: {self.casenum}, User: {self.user}, Claim Time: {self.creation_time}"
