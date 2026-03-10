from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extended user profile to store additional fields not in Django's default User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Discord ID for linking with old bot data
    discord_id = models.BigIntegerField(null=True, blank=True, unique=True)
    
    # Flag to require password reset on first login (for migrated users)
    must_reset_password = models.BooleanField(default=False)
    
    # Timestamp for when the account was migrated (null if created normally)
    migrated_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Profile for {self.user.username} (Discord: {self.discord_id})"
