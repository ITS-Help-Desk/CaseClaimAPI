# Generated by Django 5.1.7 on 2025-04-09 21:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviewedclaim', '0005_alter_reviewedclaim_lead_alter_reviewedclaim_tech'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reviewedclaim',
            old_name='lead',
            new_name='lead_id',
        ),
        migrations.RenameField(
            model_name='reviewedclaim',
            old_name='tech',
            new_name='tech_id',
        ),
    ]
