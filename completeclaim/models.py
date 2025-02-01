from django.db import models


class CompleteClaim(models.Model):
    casenum = models.CharField(max_length=8)
    user = models.CharField(max_length=256)

    claim_time = models.DateTimeField()
    complete_time = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"ID: {self.pk}, Casenum: {self.casenum}, User: {self.user}, Claim Time: {self.claim_time}, Complete Time: {self.complete_time}"
