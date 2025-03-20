from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
import json
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Count

# Create your views here.
from django.views.generic import TemplateView
from .models import Testimonial, MembershipType, CustomUser, UserProfile, Membership, Contact, Event, Module, EventBooking, ModuleEnrollment
from django import forms
from django.db.models import Count
from django.db.utils import IntegrityError

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testimonials'] = Testimonial.objects.all()
        context['membership_types'] = MembershipType.objects.all()
        return context

def login_choice(request):
    return render(request, 'login_choice.html')

def login_view(request):
    login_type = request.GET.get('type')
    context = {'login_type': login_type}
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        login_type = request.POST.get('login_type')
        
        if not username or not password:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'login_form.html', context)
        
        try:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if login_type == 'admin' and not user.is_staff:
                    messages.error(request, 'You are not authorized as an admin.')
                    return render(request, 'login_form.html', context)
                
                login(request, user)
                
                if user.is_staff and login_type == 'admin':
                    return redirect('admin:index')
                else:
                    return redirect('tc_app:member_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
                return render(request, 'login_form.html', context)
                
        except Exception as e:
            messages.error(request, 'An error occurred during login. Please try again.')
            return render(request, 'login_form.html', context)
    
    return render(request, 'login_form.html', context)

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
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if not all([username, email, password1, password2]):
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'signup.html')
            
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')
            
        try:
            # Check if username exists
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Username is already taken.')
                return render(request, 'signup.html')
                
            # Check if email exists
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Email is already registered.')
                return render(request, 'signup.html')
                
            # Create user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('tc_app:login_choice')
            
        except Exception as e:
            messages.error(request, 'An error occurred during signup. Please try again.')
            return render(request, 'signup.html')
    
    return render(request, 'signup.html')

def membership_view(request):
    membership_types = MembershipType.objects.all()
    current_membership = None
    is_authenticated = request.user.is_authenticated

    if is_authenticated:
        current_membership = Membership.objects.filter(user=request.user).first()

    if request.method == 'POST':
        if is_authenticated:
            # Existing membership update logic
            membership_type_id = request.POST.get('membership_type')
            try:
                membership_type = MembershipType.objects.get(id=int(membership_type_id))
                
                start_date = timezone.now()
                end_date = start_date + relativedelta(months=membership_type.duration)
                
                membership, created = Membership.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'membership_type': membership_type,
                        'start_date': start_date,
                        'end_date': end_date,
                        'status': 'pending'
                    }
                )
                
                messages.success(request, 'Your membership plan has been updated successfully!')
                return redirect('tc_app:profile')
                
            except (MembershipType.DoesNotExist, ValueError) as e:
                messages.error(request, 'Invalid membership type selected. Please try again.')
        else:
            # Registration logic for non-authenticated users
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            location = request.POST.get('location')
            membership_type_id = request.POST.get('membership_type')

            try:
                # Create user
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                # Create membership
                membership_type = MembershipType.objects.get(id=int(membership_type_id))
                Membership.objects.create(
                    user=user,
                    full_name=full_name,
                    email=email,
                    phone_number=phone,
                    location=location,
                    membership_type=membership_type,
                    status='pending'
                )

                # Log the user in
                login(request, user)
                messages.success(request, 'Registration successful! Your membership is pending approval.')
                return redirect('tc_app:profile')

            except IntegrityError:
                messages.error(request, 'Username or email already exists. Please try again.')
            except Exception as e:
                messages.error(request, 'An error occurred during registration. Please try again.')
    
    context = {
        'membership_types': membership_types,
        'current_membership': current_membership,
        'is_authenticated': is_authenticated
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
    except Membership.DoesNotExist:
        membership = None

    context = {
        'user': request.user,
        'membership': membership
    }
    return render(request, 'profile.html', context)

@login_required
def select_membership(request):
    if request.method == 'POST':
        membership_type_id = request.POST.get('membership_type')
        try:
            membership_type = MembershipType.objects.get(id=membership_type_id)
            
            # Calculate end date based on membership duration
            end_date = timezone.now() + timezone.timedelta(days=30 * membership_type.duration)
            
            # Update or create membership
            Membership.objects.update_or_create(
                user=request.user,
                defaults={
                    'membership_type': membership_type,
                    'end_date': end_date,
                    'status': 'active'
                }
            )
            
            messages.success(request, f'Successfully subscribed to {membership_type.name} plan!')
            return redirect('tc_app:membership')
            
        except MembershipType.DoesNotExist:
            messages.error(request, 'Invalid membership type selected.')
            
    return redirect('tc_app:membership')

@login_required
def edit_profile_view(request):
    try:
        # Try to get existing membership or create a new one
        membership, created = Membership.objects.get_or_create(
            user=request.user,
            defaults={
                'membership_type': MembershipType.objects.first(),  # Default membership type
                'status': 'pending'
            }
        )

        if request.method == 'POST':
            # Handle profile image upload
            if 'profile_image' in request.FILES:
                membership.profile_image = request.FILES['profile_image']
            
            # Update other fields
            membership.full_name = request.POST.get('full_name', '')
            membership.email = request.POST.get('email', '')
            membership.phone_number = request.POST.get('phone_number', '')
            membership.location = request.POST.get('location', '')
            membership.bio = request.POST.get('bio', '')
            membership.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('tc_app:profile')

        context = {
            'membership': membership,
        }
        return render(request, 'edit_profile.html', context)

    except Exception as e:
        messages.error(request, f'An error occurred while updating your profile: {str(e)}')
        return redirect('tc_app:profile')

@login_required
@require_http_methods(["GET", "POST"])
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('tc_app:login_choice')
    return render(request, 'logout_confirm.html')

def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin:index')
        context = {
            'user': request.user,
        }
        return render(request, 'home.html', context)
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

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin, login_url='tc_app:login')
def dashboard_view(request):
    # If user is admin, redirect to admin dashboard
    if request.user.is_staff:
        return redirect('/admin/')  # Redirect to Django admin
    # For regular users, show regular dashboard
    return render(request, 'dashboard.html')

def about_view(request):
    return render(request, 'about.html')

def events_view(request):
    # Just get all upcoming events without categorization
    upcoming_events = Event.objects.filter(status='upcoming').order_by('date')
    
    context = {
        'upcoming_events': upcoming_events
    }
    return render(request, 'events.html', context)

@user_passes_test(is_admin, login_url='tc_app:login')
def admin_dashboard(request):
    # Get actual counts from database
    context = {
        'total_members': Membership.objects.count(),
        'total_events': Event.objects.count(),
        'modules': Module.objects.filter(status='active').order_by('-created_at')[:3],
        'upcoming_events': Event.objects.filter(
            status='upcoming'
        ).order_by('date')[:3],
        'ongoing_events': Event.objects.filter(
            status='ongoing'
        ).order_by('date')[:3],
        'completed_events': Event.objects.filter(
            status='completed'
        ).order_by('-date')[:3]
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def member_dashboard(request):
    try:
        membership = Membership.objects.get(user=request.user)
    except Membership.DoesNotExist:
        membership = None

    # Get upcoming events with booking status
    upcoming_events = Event.objects.filter(status='upcoming').order_by('date')[:3]
    
    # Add booking status for each event
    for event in upcoming_events:
        event.is_booked = EventBooking.objects.filter(
            user=request.user,
            event=event,
            status='confirmed'
        ).exists()

    # Get active modules with enrollment status
    active_modules = Module.objects.filter(status='active').order_by('-created_at')[:4]
    
    # Add enrollment status for each module
    for module in active_modules:
        enrollment = ModuleEnrollment.objects.filter(
            user=request.user,
            module=module
        ).first()
        module.is_enrolled = enrollment is not None
        module.progress = enrollment.progress if enrollment else 0
        module.enrollment_status = enrollment.status if enrollment else None

    # Get user stats
    completed_modules_count = ModuleEnrollment.objects.filter(
        user=request.user,
        status='completed'
    ).count()

    booked_events_count = EventBooking.objects.filter(
        user=request.user,
        status='confirmed'
    ).count()

    context = {
        'membership': membership,
        'upcoming_events': upcoming_events,
        'active_modules': active_modules,
        'completed_modules_count': completed_modules_count,
        'booked_events_count': booked_events_count,
    }
    
    return render(request, 'member_dashboard.html', context)

@login_required
def event_detail_api(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
        is_booked = EventBooking.objects.filter(
            user=request.user,
            event=event,
            status='confirmed'
        ).exists()
        
        return JsonResponse({
            'id': event.id,
            'title': event.title,
            'date': event.date.strftime('%B %d, %Y'),
            'location': event.location,
            'description': event.description,
            'is_booked': is_booked
        })
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)

@login_required
@require_POST
def book_event(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
        
        # Check if already booked
        if EventBooking.objects.filter(user=request.user, event=event).exists():
            return JsonResponse({'error': 'You have already booked this event'}, status=400)
        
        # Create booking
        EventBooking.objects.create(
            user=request.user,
            event=event,
            status='confirmed'
        )
        
        return JsonResponse({'success': True})
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)

@login_required
@require_POST
def enroll_module(request, module_id):
    try:
        module = Module.objects.get(id=module_id)
        
        # Check if already enrolled
        if ModuleEnrollment.objects.filter(user=request.user, module=module).exists():
            return JsonResponse({'error': 'You are already enrolled in this module'}, status=400)
        
        # Create enrollment
        ModuleEnrollment.objects.create(
            user=request.user,
            module=module,
            status='enrolled'
        )
        
        return JsonResponse({'success': True})
    except Module.DoesNotExist:
        return JsonResponse({'error': 'Module not found'}, status=404)

@login_required
def module_content_view(request, module_id):
    try:
        module = Module.objects.get(id=module_id)
        enrollment = ModuleEnrollment.objects.get(user=request.user, module=module)
        
        context = {
            'module': module,
            'enrollment': enrollment,
        }
        return render(request, 'module_content.html', context)
    except Module.DoesNotExist:
        messages.error(request, 'Module not found.')
        return redirect('tc_app:member_dashboard')
    except ModuleEnrollment.DoesNotExist:
        messages.error(request, 'You are not enrolled in this module.')
        return redirect('tc_app:member_dashboard')

@login_required
@require_POST
def update_module_progress(request, module_id):
    try:
        # Parse the JSON data from request body
        data = json.loads(request.body)
        progress = data.get('progress', 0)
        status = data.get('status', 'in_progress')
        
        # Get the module and enrollment
        module = Module.objects.get(id=module_id)
        enrollment = ModuleEnrollment.objects.get(user=request.user, module=module)
        
        # Update progress and status
        enrollment.progress = progress
        enrollment.status = status
        enrollment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Module completed successfully!'
        })
        
    except (Module.DoesNotExist, ModuleEnrollment.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Module or enrollment not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def all_modules_view(request):
    # Get all active modules
    modules = Module.objects.filter(status='active').order_by('-created_at')
    
    # Add enrollment status for each module
    for module in modules:
        enrollment = ModuleEnrollment.objects.filter(
            user=request.user,
            module=module
        ).first()
        module.is_enrolled = enrollment is not None
        module.progress = enrollment.progress if enrollment else 0
        module.enrollment_status = enrollment.status if enrollment else None

    context = {
        'modules': modules
    }
    
    return render(request, 'all_modules.html', context)

@login_required
def toggle_event_notification(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
        # Toggle notification preference
        # Implement your notification logic here
        return JsonResponse({'success': True})
    except Event.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Event not found'})

def subscribe_newsletter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            # Add your email subscription logic here
            # For example, save to database or integrate with email service
            
            return JsonResponse({
                'success': True,
                'message': 'Successfully subscribed to newsletter'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    return JsonResponse({'success': False, 'message': 'Invalid request method'})