from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileSettingsForm, SignUpForm
from .models import User


def signup(request):
    if request.user.is_authenticated:
        return redirect('boards:board_list')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Witaj, {user.username}! Konto zostało utworzone.')
            return redirect('boards:board_list')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username, is_active=True)
    recent_posts = profile_user.posts.select_related('thread__board').order_by('-created_at')[:10]
    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'recent_posts': recent_posts,
    })


@login_required
def settings_view(request):
    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ustawienia zapisane.')
            return redirect('accounts:settings')
    else:
        form = ProfileSettingsForm(instance=request.user)
    return render(request, 'accounts/settings.html', {'form': form})


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Hasło zostało zmienione.')
            return redirect('accounts:settings')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/password_change.html', {'form': form})
