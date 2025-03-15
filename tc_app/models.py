from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import json

# Create your models here.
from django.db import models

class Testimonial(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ]
    
    name = models.CharField(max_length=100, null=True, blank=True, default='Anonymous')
    role = models.CharField(max_length=100, null=True, blank=True, default='Member')
    content = models.TextField(null=True, blank=True, default='No content provided')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    image = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name or 'Anonymous'} - {self.role or 'No Role'}"

class MembershipType(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, default='Basic')
    description = models.TextField(null=True, blank=True, default='Basic membership type')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name or 'Unnamed Type'

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
    # Already inherits username, email, is_staff, date_joined from AbstractUser
    pass

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Membership(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, null=True, blank=True, default='')
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True, default='')
    membership_type = models.ForeignKey(MembershipType, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.full_name or self.user.username

    def save(self, *args, **kwargs):
        if not self.email and self.user:
            self.email = self.user.email
        if not self.full_name and self.user:
            self.full_name = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
        super().save(*args, **kwargs)

class Event(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    title = models.CharField(max_length=200, null=True, blank=True, default='Untitled Event')
    description = models.TextField(null=True, blank=True, default='No description provided')
    date = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=200, null=True, blank=True, default='TBD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title or 'Untitled Event'

class Module(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ]
    
    title = models.CharField(max_length=200, null=True, blank=True, default='Untitled Module')
    description = models.TextField(null=True, blank=True, default='No description provided')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='modules/', null=True, blank=True)

    def __str__(self):
        return self.title or 'Untitled Module'

class Contact(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, default='Anonymous')
    email = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=200, null=True, blank=True, default='General Inquiry')
    message = models.TextField(null=True, blank=True, default='No message provided')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name or 'Anonymous'} - {self.subject or 'No Subject'}"

class EventBooking(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    booking_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    
    class Meta:
        unique_together = ('user', 'event')

class ModuleEnrollment(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    module = models.ForeignKey('Module', on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(default=timezone.now)
    progress = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('enrolled', 'Enrolled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='enrolled')

    class Meta:
        unique_together = ('user', 'module')
    