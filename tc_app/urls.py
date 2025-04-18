from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .admin import admin_site

app_name = 'tc_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('login-choice/', views.login_choice, name='login_choice'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('membership/', views.membership_view, name='membership'),
    path('contact/', views.contact_view, name='contact'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('about/', views.about_view, name='about'),
    path('events/', views.events_view, name='events'),
    path('admin/home/', admin_site.index, name='admin-home'),
    path('member-dashboard/', views.member_dashboard, name='member_dashboard'),
    path('api/events/<int:event_id>/', views.event_detail_api, name='event_detail_api'),
    path('api/events/<int:event_id>/book/', views.book_event, name='book_event'),
    path('api/modules/<int:module_id>/enroll/', views.enroll_module, name='enroll_module'),
    path('modules/<int:module_id>/', views.module_content_view, name='module_content'),
    path('api/modules/<int:module_id>/progress/', views.update_module_progress, name='update_module_progress'),
    path('modules/all/', views.all_modules_view, name='all_modules'),
    path('select-membership/', views.select_membership, name='select_membership'),
    path('api/events/<int:event_id>/notify/', views.toggle_event_notification, name='toggle_event_notification'),
    path('api/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
]