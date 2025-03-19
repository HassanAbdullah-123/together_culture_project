# Generated by Django 5.1.7 on 2025-03-19 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tc_app', '0017_alter_eventbooking_unique_together_event_capacity_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='eventbooking',
            unique_together={('user', 'event')},
        ),
        migrations.RemoveField(
            model_name='event',
            name='capacity',
        ),
        migrations.AddField(
            model_name='eventbooking',
            name='status',
            field=models.CharField(choices=[('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'), ('pending', 'Pending')], default='confirmed', max_length=20),
        ),
    ]
