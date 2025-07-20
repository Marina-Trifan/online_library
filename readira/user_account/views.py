from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from user_account.forms import SignUpForm

# functional view
# def main_page(request):
#     return render(request, template_name="main_page.html", context={"n": range(5)})

def logout_view(request):
    logout(request)
    return redirect('login')

# Class-Based view (CBV)

class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('index')


    
class RegisterView(CreateView):
    template_name = 'register.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')