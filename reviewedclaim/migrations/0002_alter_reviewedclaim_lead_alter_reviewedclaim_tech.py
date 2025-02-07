# Generated by Django 5.1.5 on 2025-02-07 16:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviewedclaim', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewedclaim',
            name='lead',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lead', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='reviewedclaim',
            name='tech',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tech', to=settings.AUTH_USER_MODEL),
        ),
    ]
