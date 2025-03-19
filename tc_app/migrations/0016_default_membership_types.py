from django.db import migrations

def create_default_membership_types(apps, schema_editor):
    MembershipType = apps.get_model('tc_app', 'MembershipType')
    
    default_types = [
        {
            'name': 'Basic',
            'description': 'Basic membership with standard features',
            'price': 29.99,
            'duration': 1  # 1 month
        },
        {
            'name': 'Premium',
            'description': 'Premium membership with additional benefits',
            'price': 49.99,
            'duration': 3  # 3 months
        },
        {
            'name': 'Professional',
            'description': 'Professional membership with full access',
            'price': 99.99,
            'duration': 12  # 12 months
        }
    ]
    
    for type_data in default_types:
        MembershipType.objects.get_or_create(
            name=type_data['name'],
            defaults={
                'description': type_data['description'],
                'price': type_data['price'],
                'duration': type_data['duration']
            }
        )

def reverse_default_membership_types(apps, schema_editor):
    MembershipType = apps.get_model('tc_app', 'MembershipType')
    MembershipType.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('tc_app', '0015_membership_bio_membership_location'),  # Update this to your latest migration
    ]

    operations = [
        migrations.RunPython(create_default_membership_types, reverse_default_membership_types),
    ] 