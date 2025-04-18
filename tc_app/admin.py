from django.contrib import admin
from django.shortcuts import render
from .models import CustomUser, Membership, MembershipType, Event, Module, Contact, Testimonial
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from dateutil.relativedelta import relativedelta

class CustomAdminSite(admin.AdminSite):
    site_header = 'Together Culture Administration'
    site_title = 'Together Culture Admin'
    index_title = 'Dashboard'
    
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        return app_list

    def each_context(self, request):
        context = super().each_context(request)
        context['site_url'] = '/admin/'  # Override the site_url to point to admin
        return context

    def index(self, request, extra_context=None):
        # Get all the counts and data for the dashboard
        context = {
            'total_members': Membership.objects.count(),
            'pending_approvals': Membership.objects.filter(status='pending').count(),
            'pending_memberships': Membership.objects.filter(status='pending'),
            'active_events': Event.objects.filter(status__in=['upcoming', 'ongoing']).count(),
            'active_modules': Module.objects.filter(status='active').count(),
            'upcoming_events': Event.objects.filter(status='upcoming'),
            'ongoing_events': Event.objects.filter(status='ongoing'),
            'completed_events': Event.objects.filter(status='completed'),
            'modules_list': Module.objects.filter(status='active'),
            'has_permission': True,
            'site_url': '/admin/',  # Set site_url here as well
            **(extra_context or {})
        }
        
        # Use your existing custom dashboard template
        return render(request, 'admin/custom_admin_dashboard.html', context)

    def home(self, request):
        # Get all the counts and data for the dashboard
        context = {
            'total_members': Membership.objects.count(),
            'pending_approvals': Membership.objects.filter(status='pending').count(),
            'active_events': Event.objects.filter(status__in=['upcoming', 'ongoing']).count(),
            'active_modules': Module.objects.filter(status='active').count(),
            'has_permission': True,
            'available_apps': self.get_app_list(request),
            'site_url': reverse('admin:admin-home'),
        }
        return render(request, 'admin/admin_home.html', context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('home/', self.admin_view(self.home), name='admin-home'),
            path('dashboard/', self.admin_view(self.admin_dashboard), name='admin-dashboard'),
            path('membership/<int:membership_id>/approve/',
                 self.admin_view(self.approve_membership),
                 name='approve-membership'),
            path('membership/<int:membership_id>/reject/',
                 self.admin_view(self.reject_membership),
                 name='reject-membership'),
        ]
        return custom_urls + urls

    def approve_membership(self, request, membership_id):
        try:
            membership = Membership.objects.get(id=membership_id)
            membership.status = 'approved'
            membership.start_date = timezone.now()
            membership.end_date = timezone.now() + timezone.timedelta(days=30)
            membership.save()
            
            # Send notification to user (optional)
            messages.success(request, f'Membership for {membership.user.username} has been approved.')
        except Membership.DoesNotExist:
            messages.error(request, 'Membership not found.')
        return HttpResponseRedirect('/admin/')

    def reject_membership(self, request, membership_id):
        try:
            membership = Membership.objects.get(id=membership_id)
            membership.status = 'rejected'
            membership.save()
            messages.success(request, f'Membership for {membership.user.username} has been rejected.')
        except Membership.DoesNotExist:
            messages.error(request, 'Membership not found.')
        return HttpResponseRedirect('/admin/')

    def admin_dashboard(self, request):
        context = {
            'total_members': Membership.objects.count(),
            'total_events': Event.objects.count(),
            'modules': Module.objects.filter(status='active').order_by('-created_at')[:3],
            'upcoming_events': Event.objects.filter(status='upcoming').order_by('date')[:3],
            'ongoing_events': Event.objects.filter(status='ongoing').order_by('date')[:3],
            'completed_events': Event.objects.filter(status='completed').order_by('-date')[:3]
        }
        return render(request, 'admin/custom_admin_dashboard.html', context)

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'membership_type', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'membership_type')
    search_fields = ('user__username', 'full_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
    fields = ('user', 'full_name', 'email', 'phone_number', 'location', 'bio', 'profile_image', 
             'membership_type', 'status', 'start_date', 'end_date', 'created_at', 'updated_at')
    
    actions = ['approve_selected', 'reject_selected']
    
    def approve_selected(self, request, queryset):
        for membership in queryset:
            if membership.membership_type:  # Only approve if membership type exists
                membership.status = 'approved'
                membership.start_date = timezone.now()
                membership.end_date = timezone.now() + timezone.timedelta(days=30 * membership.membership_type.duration)
                membership.save()
        self.message_user(request, f'{queryset.count()} memberships were approved.')
    approve_selected.short_description = "Approve selected memberships"
    
    def reject_selected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'{queryset.count()} memberships were rejected.')
    reject_selected.short_description = "Reject selected memberships"

class EventAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ['css/event-form.css']
        }

# Create instance of custom admin site
admin_site = CustomAdminSite(name='admin')

# Register your models with the custom admin site
admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(Membership, MembershipAdmin)
admin_site.register(MembershipType)
admin_site.register(Event, EventAdmin)
admin_site.register(Module)
admin_site.register(Contact)
admin_site.register(Testimonial)

# Export the admin_site
default_admin_site = admin_site