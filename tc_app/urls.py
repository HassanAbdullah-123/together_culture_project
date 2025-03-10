from django.urls import path
from . import views

app_name = 'tc_app'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
]