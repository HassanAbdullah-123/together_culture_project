from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from dateutil.relativedelta import relativedelta
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

def get_default_end_date():
    return timezone.now() + relativedelta(months=1)

class MembershipType(models.Model):
    MEMBERSHIP_CODES = [
        ('community', 'Community Member'),
        ('key_access', 'Key Access Member'),
        ('workspace', 'Creative Workspace Member')
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=50,
        choices=MEMBERSHIP_CODES,
        default='community'  # Set default value
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(
        help_text="Duration in months",
        default=1
    )
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Membership Type"
        verbose_name_plural = "Membership Types"

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
    full_name = models.CharField(max_length=100, default='', blank=False)
    email = models.EmailField(default='', blank=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Membership'
        verbose_name_plural = 'Memberships'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name}'s Membership"

    def save(self, *args, **kwargs):
        # Ensure email matches user email if not set
        if not self.email and self.user:
            self.email = self.user.email
        # Ensure full_name is set if not provided
        if not self.full_name and self.user:
            self.full_name = self.user.get_full_name() or self.user.username
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == 'active'

class Event(models.Model):
    EVENT_STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    EVENT_CATEGORIES = [
        ('community_meetup', 'Community Meetup'),
        ('cultural_festival', 'Cultural Festival'),
        ('workshop', 'Workshop'),
    ]
    
    title = models.CharField(max_length=200, default='Untitled Event')
    description = models.TextField(default='Event description coming soon.')
    date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    location = models.CharField(max_length=200, default='To be announced')
    status = models.CharField(
        max_length=20, 
        choices=EVENT_STATUS_CHOICES,
        default='upcoming'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(
        max_length=50, 
        choices=EVENT_CATEGORIES,
        default='community_meetup'
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date']

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
    