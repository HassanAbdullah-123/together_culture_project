from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'tc_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('membership/', views.membership_view, name='membership'),
]