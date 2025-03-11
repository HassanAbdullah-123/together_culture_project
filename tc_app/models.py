from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

# Create your models here.
from django.db import models

class Testimonial(models.Model):
    name = models.CharField(max_length=100, default='Anonymous')
    role = models.CharField(max_length=100, blank=True, null=True, default='')
    content = models.TextField()
    date_added = models.DateTimeField(default=timezone.now)
    is_featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)

    def __str__(self):
        return f"Testimonial by {self.name}"

class MembershipType(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(
        max_length=10, 
        unique=True,
        blank=True  # Remove default, we'll handle it in save()
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00
    )
    duration_months = models.PositiveIntegerField(default=1)
    description = models.TextField(null=True, blank=True)
    features = models.JSONField(default=list, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)  # For sorting

    class Meta:
        verbose_name = 'Membership Type'
        verbose_name_plural = 'Membership Types'
        ordering = ['order', 'price']

    def __str__(self):
        return f"{self.name} - ${self.price}/month"

    def save(self, *args, **kwargs):
        if not self.code:
            # Generate a unique code
            while True:
                new_code = str(uuid.uuid4())[:8].upper()
                if not MembershipType.objects.filter(code=new_code).exists():
                    self.code = new_code
                    break
        super().save(*args, **kwargs)

    @property
    def monthly_price(self):
        return self.price / self.duration_months if self.duration_months > 0 else self.price

class MembershipBenefit(models.Model):
    membership_type = models.ForeignKey(
        MembershipType, 
        on_delete=models.CASCADE, 
        related_name='benefits'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    icon = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        default='fas fa-check'  # Default FontAwesome icon
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    order = models.PositiveIntegerField(default=0)  # For sorting benefits

    class Meta:
        verbose_name = 'Membership Benefit'
        verbose_name_plural = 'Membership Benefits'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.membership_type.name} - {self.name}"

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    objects = CustomUserManager()
    
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs):
        if self.is_admin:
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Membership(models.Model):
    MEMBERSHIP_TYPES = [
        ('FREE', 'Free'),
        ('BASIC', 'Basic'),
        ('PREMIUM', 'Premium'),
        ('PRO', 'Professional')
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    membership_type = models.CharField(
        max_length=10,
        choices=MEMBERSHIP_TYPES,
        default='FREE'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    interests = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = 'Membership'
        verbose_name_plural = 'Memberships'

    def __str__(self):
        return f"{self.user.username}'s {self.get_membership_type_display()} Membership"

    @property
    def is_active(self):
        if self.expiration_date:
            return timezone.now() <= self.expiration_date
        return True

    def save(self, *args, **kwargs):
        # Set email from user if not provided
        if not self.email and self.user.email:
            self.email = self.user.email
        # Set full_name from user if not provided
        if not self.full_name and (self.user.first_name or self.user.last_name):
            self.full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        super().save(*args, **kwargs)

    def get_interests(self):
        return self.interests if self.interests else []

# Signal to create membership when user is created
@receiver(post_save, sender=CustomUser)
def create_user_membership(sender, instance, created, **kwargs):
    if created:
        Membership.objects.create(
            user=instance,
            email=instance.email,
            full_name=f"{instance.first_name} {instance.last_name}".strip() if instance.first_name or instance.last_name else None,
            membership_type='FREE',
            created_at=instance.date_joined
        )

@receiver(post_save, sender=CustomUser)
def save_user_membership(sender, instance, **kwargs):
    try:
        if not hasattr(instance, 'membership'):
            Membership.objects.create(
                user=instance,
                email=instance.email,
                full_name=f"{instance.first_name} {instance.last_name}".strip() if instance.first_name or instance.last_name else None,
                membership_type='FREE',
                created_at=instance.date_joined
            )
        else:
            instance.membership.save()
    except Exception as e:
        print(f"Error saving membership: {e}")

# If you have an Event model
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    date = models.DateTimeField()
    location = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    organizer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return self.title

# If you have a Module model
class Module(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(
        blank=True,
        null=True,
        default=''
    )
    content = models.TextField()
    order = models.PositiveIntegerField(
        default=0
    )
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        default=timezone.now
    )
    image = models.ImageField(
        upload_to='modules/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    responded = models.BooleanField(default=False)
    response_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    def __str__(self):
        return f"{self.name} - {self.subject}"
    