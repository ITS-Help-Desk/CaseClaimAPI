from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ParentCase(models.Model):
    case_number = models.CharField(unique=True, max_length=8)
    description = models.TextField()
    solution = models.TextField(null=True)
    active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
    
    def __str__(self):
        return f"ID: {self.pk}, Casenum: {self.case_number}, User ID: {self.user_id}, Description: {self.description}"
