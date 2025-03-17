# Generated by Django 5.1.7 on 2025-03-15 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tc_app', '0011_membership_email_membership_full_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='membershiptype',
            options={'verbose_name': 'Membership Type', 'verbose_name_plural': 'Membership Types'},
        ),
        migrations.RemoveField(
            model_name='membershiptype',
            name='features',
        ),
        migrations.AddField(
            model_name='membershiptype',
            name='code',
            field=models.CharField(choices=[('community', 'Community Member'), ('key_access', 'Key Access Member'), ('workspace', 'Creative Workspace Member')], default='community', max_length=50),
        ),
        migrations.AlterField(
            model_name='membershiptype',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='membershiptype',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='membershiptype',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
