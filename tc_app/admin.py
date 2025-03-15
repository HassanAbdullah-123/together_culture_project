from django.contrib import admin
from django.shortcuts import render
from .models import CustomUser, Membership, MembershipType, Event, Module, Contact, Testimonial

class CustomAdminSite(admin.AdminSite):
    site_header = 'Together Culture Administration'
    site_title = 'Together Culture Admin'
    index_title = 'Dashboard'  # This will be shown at the top of the dashboard

    def index(self, request, extra_context=None):
        # Get all the counts and data for the dashboard
        context = {
            'total_members': Membership.objects.count(),
            'pending_approvals': Membership.objects.filter(status='pending').count(),
            'active_events': Event.objects.filter(status__in=['upcoming', 'ongoing']).count(),
            'active_modules': Module.objects.filter(status='active').count(),
            'upcoming_events': Event.objects.filter(status='upcoming'),
            'ongoing_events': Event.objects.filter(status='ongoing'),
            'completed_events': Event.objects.filter(status='completed'),
            'modules_list': Module.objects.filter(status='active'),
            'has_permission': True,
            'site_url': '/',
            **(extra_context or {})
        }
        
        # Use your existing custom dashboard template
        return render(request, 'admin/custom_admin_dashboard.html', context)

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

# Create instance of custom admin site
admin_site = CustomAdminSite(name='admin')

# Register your models with the custom admin site
admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(Membership)
admin_site.register(MembershipType)
admin_site.register(Event)
admin_site.register(Module)
admin_site.register(Contact)
admin_site.register(Testimonial)

# Export the admin_site
default_admin_site = admin_site