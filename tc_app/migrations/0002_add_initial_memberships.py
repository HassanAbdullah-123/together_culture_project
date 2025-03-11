from django.db import migrations

def create_initial_membership_types(apps, schema_editor):
    MembershipType = apps.get_model('tc_app', 'MembershipType')
    MembershipBenefit = apps.get_model('tc_app', 'MembershipBenefit')

    # Clear existing data to avoid duplicates
    MembershipBenefit.objects.all().delete()
    MembershipType.objects.all().delete()

    # Create membership types
    free = MembershipType.objects.create(
        name='Free',
        code='FREE',
        price=0.00,
        description='Basic membership with limited features',
        features=['Basic access', 'Community forums'],
        order=1,
        is_active=True
    )

    basic = MembershipType.objects.create(
        name='Basic',
        code='BASIC',
        price=9.99,
        description='Enhanced features for regular members',
        features=['All Free features', 'Event participation', 'Monthly newsletter'],
        order=2,
        is_active=True
    )

    premium = MembershipType.objects.create(
        name='Premium',
        code='PREMIUM',
        price=19.99,
        description='Premium features for dedicated members',
        features=['All Basic features', 'Priority support', 'Exclusive content'],
        order=3,
        is_active=True
    )

    # Create benefits for each type
    # Free benefits
    MembershipBenefit.objects.create(
        membership_type=free,
        name='Community Access',
        icon='fas fa-users',
        order=1,
        is_active=True
    )
    MembershipBenefit.objects.create(
        membership_type=free,
        name='Basic Forums',
        icon='fas fa-comments',
        order=2,
        is_active=True
    )

    # Basic benefits
    MembershipBenefit.objects.create(
        membership_type=basic,
        name='Event Access',
        icon='fas fa-calendar',
        order=1,
        is_active=True
    )
    MembershipBenefit.objects.create(
        membership_type=basic,
        name='Monthly Newsletter',
        icon='fas fa-envelope',
        order=2,
        is_active=True
    )

    # Premium benefits
    MembershipBenefit.objects.create(
        membership_type=premium,
        name='Priority Support',
        icon='fas fa-headset',
        order=1,
        is_active=True
    )
    MembershipBenefit.objects.create(
        membership_type=premium,
        name='Exclusive Content',
        icon='fas fa-star',
        order=2,
        is_active=True
    )

def remove_initial_membership_types(apps, schema_editor):
    MembershipType = apps.get_model('tc_app', 'MembershipType')
    MembershipType.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('tc_app', '0001_initial'),  # Make sure this matches your previous migration
    ]

    operations = [
        migrations.RunPython(create_initial_membership_types, remove_initial_membership_types),
    ] 