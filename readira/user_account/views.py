from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import ProfileForm



def login_view(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'invalid credentials')
    return render(request, 'user_account/login.html')

def logout_view(request):
    logout(request)
    return redirect('user_account:login')


    
class RegisterView(View):
    def get(self, request):
        return render(request, "user_account/register.html")

    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        context = {
            "username": username,
            "email": email,
        }

        if password != confirm_password:
            context["error"] = "Passwords do not match."
            return render(request, "user_account/register.html", context)

        if User.objects.filter(username=username).exists():
            context["error"] = "Username already taken."
            return render(request, "user_account/register.html", context)

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect("user_account:profile")

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=user)
        password_form = PasswordChangeForm(user, request.POST)

        if 'save_profile' in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')

        elif 'change_password' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed.')
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=user)
        password_form = PasswordChangeForm(user)

    return render(request, 'user_account/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'user_city': user.profile.city if hasattr(user, 'profile') and user.profile.city else '',
    })