from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    group_names = ["Alumni", "Tech", "Lead", "Phone Analyst", "Manager"]
    for name in group_names:
        group, created = Group.objects.get_or_create(name=name)
        if created:
            print(f"Created group: {name}")
