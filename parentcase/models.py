from django.db import models
#from .user.models import User

# Create your models here.
class ParentCase(models.Model):
    case_number = models.CharField(unique=True, max_length=8)
    description = models.TextField()
    solution = models.TextField(null=True)
    active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    user = models.TextField()
    #user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    #This line needs to be added in when we actually have a user model to go off of.