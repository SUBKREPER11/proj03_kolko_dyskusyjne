from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('rejestracja/', views.signup, name='signup'),
    path('logowanie/', auth_views.LoginView.as_view(
        template_name='accounts/login.html', redirect_authenticated_user=True,
    ), name='login'),
    path('wyloguj/', auth_views.LogoutView.as_view(), name='logout'),
    path('ustawienia/', views.settings_view, name='settings'),
    path('ustawienia/haslo/', views.password_change, name='password_change'),
    path('u/<str:username>/', views.profile, name='profile'),
]
