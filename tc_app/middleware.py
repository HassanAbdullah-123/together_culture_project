from django.shortcuts import redirect
from django.urls import resolve

class UserTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_url = resolve(request.path_info).url_name
            
            # If superuser, ensure they stay in admin interface
            if request.user.is_superuser:
                # Allow access to admin URLs
                if 'admin' in request.path:
                    return self.get_response(request)
                # Redirect to admin index for non-admin URLs
                return redirect('admin:index')
            
            # If regular user tries to access admin pages, redirect to dashboard
            if not request.user.is_superuser and 'admin' in request.path:
                return redirect('tc_app:member_dashboard')

        response = self.get_response(request)
        return response 