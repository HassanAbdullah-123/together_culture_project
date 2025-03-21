from django.contrib import admin
from django.shortcuts import render
from .models import CustomUser, Membership, MembershipType, Event, Module, Contact, Testimonial
from django.urls import path
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
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

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'full_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['approve_selected', 'reject_selected']
    
    def approve_selected(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f'{queryset.count()} memberships were approved.')
    approve_selected.short_description = "Approve selected memberships"
    
    def reject_selected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'{queryset.count()} memberships were rejected.')
    reject_selected.short_description = "Reject selected memberships"

# Create instance of custom admin site
admin_site = CustomAdminSite(name='admin')

# Register your models with the custom admin site
admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(Membership, MembershipAdmin)
admin_site.register(MembershipType)
admin_site.register(Event)
admin_site.register(Module)
admin_site.register(Contact)
admin_site.register(Testimonial)

# Export the admin_site
default_admin_site = admin_site