# Generated by Django 5.1.7 on 2025-04-09 21:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('completeclaim', '0003_alter_completeclaim_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='completeclaim',
            old_name='user',
            new_name='user_id',
        ),
    ]
