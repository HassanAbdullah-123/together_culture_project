from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import json

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
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()

    def __str__(self):
        return self.name

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
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    REQUIRED_FIELDS = ['email']

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
        ('BASIC', 'Basic'),
        ('PREMIUM', 'Premium'),
        ('PRO', 'Professional'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    membership_type = models.CharField(
        max_length=10, 
        choices=MEMBERSHIP_TYPES, 
        default='BASIC'
    )
    full_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        default=''
    )
    bio = models.TextField(
        blank=True, 
        null=True, 
        default=''
    )
    location = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        default=''
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        default=''
    )
    profile_image = models.ImageField(
        upload_to='profile_images/', 
        blank=True, 
        null=True
    )
    interests = models.TextField(default='[]', blank=True)
    join_date = models.DateTimeField(
        default=timezone.now
    )
    expiration_date = models.DateTimeField(
        null=True, 
        blank=True
    )
    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.user.username}'s Membership"

    def get_membership_type_display(self):
        return dict(self.MEMBERSHIP_TYPES).get(self.membership_type, '')

    def get_interests(self):
        """Return interests as a list"""
        try:
            return json.loads(self.interests)
        except (json.JSONDecodeError, TypeError):
            return []

# If you have an Event model
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(
        blank=True,
        null=True,
        default=''
    )
    date = models.DateTimeField()
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        default=''
    )
    image = models.ImageField(
        upload_to='events/',
        blank=True,
        null=True
    )
    capacity = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True
    )

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
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']
    