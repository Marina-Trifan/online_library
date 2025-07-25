from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .forms import CustomUserForm, CustomPasswordChangeForm
from library.models import ReadingMaterials, SubscriptionPlan

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
    return render(request, 'user_account/login.html')

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
    return render(request, 'user_account/register.html')

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


# Buy Button view
@login_required
def add_to_cart(request, material_pk):
    material = get_object_or_404(ReadingMaterials, pk=material_pk)
    cart = request.session.get('cart', {})
    key = str(material_pk)
    if key in cart:
        messages.info(request, "You already have this book in your cart.")
    else:
        cart['key'] = {
            'pk': material.pk,
            'title': material.title,
            'image': material.image.url if material.image else '',
            'price': float(material.price),
            'quantity': 1,
            'total': float(material.price)
        }
        messages.success(request, "Book added to cart.")

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('user_account:cart')

@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    materials = list(cart.values())
    total = sum(item['total'] for item in materials)
    return render(request, 'user_account/cart.html', {'materials':materials, 'total':total})


# Subscriptions view
class SubscriptionPageView(TemplateView):
    template_name = 'user_account/subscriptions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plans = SubscriptionPlan.objects.all()
        context['plans'] = plans
        return context

