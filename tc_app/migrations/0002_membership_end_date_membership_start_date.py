# Generated by Django 5.1.7 on 2025-03-23 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tc_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='membership',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
