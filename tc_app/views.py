from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json
from django.urls import reverse

# Create your views here.
from django.views.generic import TemplateView
from .models import Testimonial, MembershipType, CustomUser, UserProfile, Membership

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

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tc_app:select_membership')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def membership_view(request):
    if request.method == 'POST':
        # Get or create membership instance
        membership, created = Membership.objects.get_or_create(user=request.user)
        
        # Update membership fields
        membership.full_name = request.POST.get('full_name')
        membership.email = request.POST.get('email')
        membership.phone_number = request.POST.get('phone')
        membership.location = request.POST.get('location')
        membership.membership_type = request.POST.get('membership_type')
        
        # Handle interests
        interests = request.POST.getlist('interests[]')
        membership.interests = json.dumps(interests)
        
        # Handle profile image
        if 'profile_image' in request.FILES:
            membership.profile_image = request.FILES['profile_image']
        
        try:
            membership.save()
            messages.success(request, 'Membership details updated successfully!')
            return redirect('tc_app:profile')
        except Exception as e:
            messages.error(request, f'Error updating membership: {str(e)}')
    
    # Get existing membership data for display
    try:
        membership = Membership.objects.get(user=request.user)
    except Membership.DoesNotExist:
        membership = None

    # Get membership types from model choices
    membership_types = [
        {'code': code, 'name': name, 'description': get_membership_description(code)}
        for code, name in Membership.MEMBERSHIP_TYPES
    ]

    context = {
        'membership': membership,
        'membership_types': membership_types
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
        }
    except:
        context = {}
    
    return render(request, 'profile.html', context)

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
    if request.method == 'POST':
        membership = request.user.membership
        
        # Update all profile fields
        membership.full_name = request.POST.get('full_name', '')
        membership.email = request.POST.get('email', '')
        membership.phone_number = request.POST.get('phone_number', '')
        membership.location = request.POST.get('location', '')
        membership.bio = request.POST.get('bio', '')
        
        # Handle profile image
        if 'profile_image' in request.FILES:
            membership.profile_image = request.FILES['profile_image']
            
        # Handle interests
        interests = request.POST.getlist('interests[]')
        membership.interests = json.dumps(interests)
        
        membership.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('tc_app:profile')
        
    return render(request, 'edit_profile.html', {
        'membership': request.user.membership
    })

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