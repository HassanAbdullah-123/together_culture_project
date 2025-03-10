from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
from django.views.generic import TemplateView
from .models import Testimonial, MembershipType, CustomUser, UserProfile

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
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            is_admin = request.POST.get('is_admin') == 'on'

            # Validation
            if not all([username, email, password, confirm_password]):
                messages.error(request, 'All fields are required')
                return render(request, 'signup.html')

            # Check password match first
            if password != confirm_password:
                messages.error(request, 'Passwords do not match')
                return render(request, 'signup.html', {
                    'username': username,
                    'email': email,
                    'is_admin': is_admin
                })

            # Check if user already exists
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return render(request, 'signup.html', {
                    'email': email,
                    'is_admin': is_admin
                })

            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return render(request, 'signup.html', {
                    'username': username,
                    'is_admin': is_admin
                })

            # Create user with admin status
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Set admin status and permissions
            if is_admin:
                user.is_admin = True
                user.is_staff = True
                user.is_superuser = True
                user.save()

            # Create user profile
            UserProfile.objects.create(user=user)

            # Add success message
            messages.success(request, 'Registration successful! Please login.')
            
            # Redirect to login page
            return redirect('tc_app:login')

        except Exception as e:
            print(f"Error during signup: {str(e)}")  # For debugging
            messages.error(request, 'An error occurred during registration')
            return render(request, 'signup.html', {
                'username': username,
                'email': email,
                'is_admin': is_admin
            })

    return render(request, 'signup.html')