from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from user_account.forms import SignUpForm


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
    return redirect('login')

# Class-Based view (CBV)

# class CustomLoginView(LoginView):
#     template_name = 'login.html'
#     success_url = reverse_lazy('index')


    
class RegisterView(CreateView):
    template_name = 'register.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')