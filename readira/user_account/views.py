from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import CustomUserForm, CustomPasswordChangeForm

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('/')  # or 'dashboard', etc.
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'user_backend/login.html')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
        else:
            user = User.objects.create_user(email=email, password=password)
            login(request, user)
            return redirect('/')
    return render(request, 'user_backend/register.html')

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        if 'save_profile' in request.POST:
            profile_form = CustomUserForm(request.POST, instance=user)
            password_form = CustomPasswordChangeForm(user)
            if profile_form.is_valid():
                profile_form.save()
        elif 'change_password' in request.POST:
            profile_form = CustomUserForm(instance=user)
            password_form = CustomPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
    else:
        profile_form = CustomUserForm(instance=user)
        password_form = CustomPasswordChangeForm(user)
    return render(request, 'user_account/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')