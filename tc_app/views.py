from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
from django.views.generic import TemplateView
from .models import Testimonial, MembershipType, CustomUser, UserProfile, Membership, Contact, MembershipBenefit
from django import forms

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testimonials'] = Testimonial.objects.all()
        context['membership_types'] = MembershipType.objects.all()
        return context

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('tc_app:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('tc_app:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

@login_required
def membership_view(request):
    if request.method == 'POST':
        try:
            membership, created = Membership.objects.get_or_create(user=request.user)
            
            # Update membership details
            membership.full_name = request.POST.get('full_name')
            membership.email = request.POST.get('email')
            membership.phone_number = request.POST.get('phone')
            membership.location = request.POST.get('location')
            membership.membership_type = request.POST.get('membership_type')
            membership.bio = request.POST.get('bio', '')
            
            # Handle profile image
            if request.FILES.get('profile_image'):
                membership.profile_image = request.FILES['profile_image']
            
            # Handle interests
            interests = request.POST.getlist('interests[]')
            if interests:
                membership.interests = interests
            
            membership.save()
            
            messages.success(request, 'Membership details updated successfully!')
            return redirect('tc_app:profile')
            
        except Exception as e:
            messages.error(request, f'Error updating membership: {str(e)}')
            return redirect('tc_app:membership')
    
    # Get current membership data
    membership = Membership.objects.filter(user=request.user).first()
    membership_types = MembershipType.objects.filter(is_active=True)
    
    context = {
        'membership': membership,
        'membership_types': membership_types,
    }
    
    return render(request, 'membership.html', context)

def get_membership_description(membership_type):
    descriptions = {
        'BASIC': 'Access to community events and basic resources',
        'PREMIUM': 'Additional access to premium resources and workshops',
        'PRO': 'Full access to all resources and exclusive events'
    }
    return descriptions.get(membership_type, '')

@login_required
def profile_view(request):
    try:
        membership = request.user.membership
        context = {
            'membership': membership,
            'interests': membership.interests if membership.interests else [],
        }
        return render(request, 'profile.html', context)
    except Membership.DoesNotExist:
        messages.warning(request, 'Please complete your membership details first.')
        return redirect('tc_app:membership')

@login_required
def select_membership(request):
    if request.method == 'POST':
        membership_type = request.POST.get('membership_type')
        membership, created = Membership.objects.get_or_create(user=request.user)
        membership.membership_type = membership_type
        membership.save()
        
        if created:
            return redirect('tc_app:edit_profile')
        return redirect('tc_app:profile')
    
    membership_types = MembershipType.objects.all()
    return render(request, 'membership_plans.html', {'membership_types': membership_types})

@login_required
def edit_profile(request):
    # Get or create membership
    membership, created = Membership.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle profile image upload
        if 'profile_image' in request.FILES:
            membership.profile_image = request.FILES['profile_image']
        
        # Update other fields
        membership.full_name = request.POST.get('full_name', '')
        membership.email = request.POST.get('email', '')
        membership.phone_number = request.POST.get('phone_number', '')
        membership.bio = request.POST.get('bio', '')
        
        try:
            membership.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('tc_app:profile')
        except Exception as e:
            messages.error(request, 'Error updating profile. Please try again.')
    
    context = {
        'membership': membership
    }
    return render(request, 'edit_profile.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('tc_app:home')
    return render(request, 'logout_confirm.html')

def home(request):
    return render(request, 'home.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        try:
            # Save to database
            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )

            # Optional: Send email notification to admin
            admin_message = f"""
            New contact form submission:
            
            From: {name}
            Email: {email}
            Subject: {subject}
            Message: {message}
            """

            try:
                send_mail(
                    subject=f'New Contact Form Submission: {subject}',
                    message=admin_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
            except Exception as e:
                # Log the email error but don't stop the process
                print(f"Email notification failed: {str(e)}")

            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('tc_app:contact')
            
        except Exception as e:
            messages.error(request, 'Sorry, there was an error sending your message. Please try again.')
            print(f"Contact form error: {str(e)}")
    
    return render(request, 'contact.html')

@login_required
def dashboard_view(request):
    """
    Temporary dashboard view showing coming soon message
    """
    return render(request, 'dashboard.html')

def about_view(request):
    return render(request, 'about.html')

def events_view(request):
    return render(request, 'events.html')