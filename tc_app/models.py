from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
from django.db import models

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='testimonials/')
    testimonial_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

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
    