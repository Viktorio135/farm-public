# Generated by Django 5.1.4 on 2025-01-15 00:45

import panel.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('1', 'active'), ('0', 'archive')], default=1, max_length=1),
        ),
        migrations.AlterField(
            model_name='usertask',
            name='screenshot',
            field=models.ImageField(blank=True, null=True, upload_to=panel.models.confirmation_upload_path),
        ),
    ]
