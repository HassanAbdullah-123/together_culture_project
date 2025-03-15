from django.contrib import admin
from django.contrib.admin import AdminSite
from django.shortcuts import render
from .models import CustomUser, Membership, MembershipType, Event, Module, Contact, Testimonial

class CustomAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        # Get active modules queryset
        active_modules_queryset = Module.objects.filter(status='active')
        
        context = {
            'total_members': Membership.objects.count(),
            'pending_approvals': Membership.objects.filter(status='pending').count(),
            'active_events': Event.objects.filter(status__in=['upcoming', 'ongoing']).count(),
            'active_modules': active_modules_queryset.count(),  # Get the count instead of queryset
            'upcoming_events': Event.objects.filter(status='upcoming').order_by('date'),
            'ongoing_events': Event.objects.filter(status='ongoing').order_by('date'),
            'completed_events': Event.objects.filter(status='completed').order_by('-date'),
            'modules_list': active_modules_queryset,  # Rename to modules_list for clarity
        }
        return render(request, 'admin/custom_admin_dashboard.html', context)

# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='customadmin')

# Register models with custom admin site
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'status', 'created_at')
    list_filter = ('status', 'membership_type')
    search_fields = ('full_name', 'email')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'status')
    list_filter = ('status', 'date')
    search_fields = ('title', 'description')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'description')

# Register other models
admin.site.register(MembershipType)
admin.site.register(Contact)
admin.site.register(Testimonial)

# Register all models with custom admin site
custom_admin_site.register(CustomUser, CustomUserAdmin)
custom_admin_site.register(Membership, MembershipAdmin)
custom_admin_site.register(Event, EventAdmin)
custom_admin_site.register(Module, ModuleAdmin)
custom_admin_site.register(MembershipType)
custom_admin_site.register(Contact)
custom_admin_site.register(Testimonial)

# Customize admin site
admin.site.site_header = 'Together Culture Administration'
admin.site.site_title = 'Together Culture Admin'
admin.site.index_title = 'Welcome to Together Culture Admin Portal'