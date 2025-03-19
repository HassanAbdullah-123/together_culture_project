# Generated by Django 5.1.7 on 2025-03-19 18:02

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tc_app', '0018_alter_eventbooking_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventbooking',
            name='booking_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='eventbooking',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
        migrations.CreateModel(
            name='EventWaitlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_created=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tc_app.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Event Waitlist',
                'verbose_name_plural': 'Event Waitlists',
                'unique_together': {('user', 'event')},
            },
        ),
    ]
