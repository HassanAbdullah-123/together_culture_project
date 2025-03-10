from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'tc_app'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('membership/', views.membership_view, name='membership'),
    path('logout/', LogoutView.as_view(next_page='tc_app:home'), name='logout'),
]