"""
Django management command to set temporary passwords for migrated users.

This script sets a temporary password for all users who have must_reset_password=True
(migrated users who haven't set their password yet).

Usage:
    python manage.py set_temp_passwords
    python manage.py set_temp_passwords --password "MyCustomPassword123"
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user.models import UserProfile


DEFAULT_TEMP_PASSWORD = 'CaseFlow2026!'


class Command(BaseCommand):
    help = 'Set temporary password for all migrated users who need to reset their password'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default=DEFAULT_TEMP_PASSWORD,
            help=f'Temporary password to set (default: {DEFAULT_TEMP_PASSWORD})',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually changing passwords',
        )

    def handle(self, *args, **options):
        temp_password = options['password']
        dry_run = options['dry_run']
        
        # Find all users with must_reset_password=True
        profiles = UserProfile.objects.filter(must_reset_password=True)
        
        if not profiles.exists():
            self.stdout.write(self.style.WARNING("No users found with must_reset_password=True"))
            return
        
        self.stdout.write(self.style.NOTICE(f"{'DRY RUN - ' if dry_run else ''}Setting temporary password for {profiles.count()} users..."))
        self.stdout.write(self.style.NOTICE(f"Temporary password: {temp_password}"))
        self.stdout.write("")
        
        updated_count = 0
        
        for profile in profiles:
            user = profile.user
            
            if dry_run:
                self.stdout.write(f"  WOULD UPDATE: {user.first_name} {user.last_name} ({user.username})")
            else:
                user.set_password(temp_password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"  UPDATED: {user.first_name} {user.last_name} ({user.username})"))
            
            updated_count += 1
        
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("=" * 50))
        self.stdout.write(self.style.SUCCESS(f"Updated: {updated_count} users"))
        self.stdout.write(self.style.NOTICE("=" * 50))
        
        if not dry_run:
            self.stdout.write("")
            self.stdout.write(self.style.NOTICE(f"All migrated users can now login with:"))
            self.stdout.write(self.style.NOTICE(f"  Username: (their username)"))
            self.stdout.write(self.style.NOTICE(f"  Password: {temp_password}"))
            self.stdout.write(self.style.WARNING(f"They will be prompted to change their password on first login."))
