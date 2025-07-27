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
from library.models import ReadingMaterials, SubscriptionPlan, Order
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from datetime import datetime
import hashlib
from django.utils.crypto import get_random_string
from django.views import View
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import EmailLoginForm

User = get_user_model()

class StoreLoginView(LoginView):
    template_name = "user_account/login.html"
    authentication_form = EmailLoginForm

    def get_success_url(self):
        return reverse_lazy("user_account:profile")

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("user_account:profile")  # or wherever you want
        email = request.GET.get("email", "")
        return render(request, "user_account/register.html", {"email": email})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("user_account:profile")

        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        context = {"email": email}

        if password != confirm_password:
            context["error"] = "Passwords do not match."
            return render(request, "user_account/register.html", context)

        if User.objects.filter(email=email).exists():
            context["error"] = "Email already registered."
            return render(request, "user_account/register.html", context)

        user = User.objects.create_user(email=email, password=password)
        login(request, user)
        return redirect("user_account:cart")

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        if 'save_profile' in request.POST:
            profile_form = CustomUserForm(request.POST, instance=user)
            password_form = CustomPasswordChangeForm(user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully.')
            else:
                messages.error(request, 'Something went wrong. Please check the form fileds and try again.')
        elif 'change_password' in request.POST:
            profile_form = CustomUserForm(instance=user)
            password_form = CustomPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Password changed successfully.')
            else:
                messages.error(request, 'Something went wrong. Please check the form fileds and try again.')
    else:
        profile_form = CustomUserForm(instance=user)
        password_form = CustomPasswordChangeForm(user)

    orders = getattr(user, "orders", None)
    orders = orders.all().order_by('-submitted_at') if orders else []
    fields = ['full_name', 'phone', 'city', 'country', 'street', 'zip_code', 'avatar_url', 'preferred_channel']

    return render(request, 'user_account/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'orders': orders,
        "fields": fields
    })

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')


# Buy Button view
@login_required
def add_to_cart(request, material_id):
    material = get_object_or_404(ReadingMaterials, id=material_id)
    quantity = int(request.POST.get("quantity", 1))

    cart = request.session.get("cart", {})
    key = str(material.id)

    if key in cart:
        cart[key]["quantity"] += quantity
        cart[key]["total"] = round(cart[key]["quantity"] * float(cart[key]["price"]), 2)
    else:
        cart[key] = {
            "material_id": material.id,
            "title": material.title,
            "thumbnail": material.image.url if material.image else "",
            "price": float(material.price or 0),
            "quantity": quantity,
            "total": round(float(material.price or 0) * quantity, 2),
        }

    # Ensure token is created only once
    if "order_token" not in request.session:
        raw = f"{request.user.id}-{get_random_string(12)}"
        token = hashlib.sha256(raw.encode()).hexdigest()
        request.session["order_token"] = token

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("user_account:cart")

@login_required
def cart_view(request):
    cart = request.session.get("cart", {})
    materials = []
    total = 0

    for item in cart.values():
        try:
            material = ReadingMaterials.objects.get(pk=item["material_id"])
            material.quantity = item["quantity"]
            material.total = item["total"]
            materials.append(material)
            total += material.total
        except ReadingMaterials.DoesNotExist:
            continue

    order_token = request.session.get("order_token")
    return render(request, "user_account/cart.html", {
        "materials": materials,
        "total_price": total,
        "order_token": order_token,
    })

@require_POST
def remove_from_cart(request, material_id):
    cart = request.session.get("cart", {})
    material_key = str(material_id)
    if material_key in cart:
        del cart[material_key]
        request.session.modified = True
    return redirect('user_account:cart')

@require_http_methods(["GET", "POST"])
@login_required
def checkout_view(request, token):
    cart = request.session.get("cart", {})
    session_token = request.session.get("order_token")

    if not cart or session_token != token:
        messages.error(request, "Invalid or expired checkout session.")
        return redirect("user_account:cart")

    total_price = sum(item["total"] for item in cart.values())

    if request.method == "POST":
        # Validate fields (same as before)
        cardholder_name = request.POST.get("cardholder_name", "").strip()
        card_number = request.POST.get("card_number", "").strip()
        card_expiry = request.POST.get("card_expiry", "").strip()
        card_cvv = request.POST.get("card_cvv", "").strip()
        errors = []

        if not card_number.isdigit() or len(card_number) != 16:
            errors.append("Card number must be exactly 16 digits.")
        if len(cardholder_name.split()) < 2:
            errors.append("Cardholder name must contain at least two names.")
        if not card_expiry or len(card_expiry) != 5 or card_expiry[2] != '/':
            errors.append("Expiration date must be in MM/YY format.")
        else:
            try:
                month, year = map(int, card_expiry.split('/'))
                expiry_date = datetime.strptime(f"{month}/20{year}", "%m/%Y")
                if expiry_date < datetime.now().replace(day=1):
                    errors.append("Card expiry must be in the future.")
            except ValueError:
                errors.append("Invalid expiration date format.")
        if not card_cvv.isdigit() or len(card_cvv) != 3:
            errors.append("CVV must be exactly 3 digits.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, "user_account/checkout.html", {
                "total_price": total_price,
                "order_token": token
            })

        # Create orders
        for item in cart.values():
            Order.objects.create(
                user=request.user,
                client_full_name=cardholder_name,
                delivery_address=request.user.street,
                user_address=request.user.city,
                reading_material=ReadingMaterials.objects.get(id=item["material_id"]),
                quantity=item["quantity"],
                price_per_item=item["price"],
                card_number=card_number,
                card_expiry=card_expiry,
                card_cvv=card_cvv,
                cardholder_name=cardholder_name,
                buy_session_hash=hashlib.sha256(
                    f"{card_number}{card_expiry}{cardholder_name}{get_random_string(8)}".encode()
                ).hexdigest(),
                status=Order.Status.PAID,
            )

        # Finalize: clear cart + token
        request.session.pop("cart", None)
        request.session.pop("order_token", None)
        request.session.modified = True

        return redirect("user_account:checkout_success")

    return render(request, "user_account/checkout.html", {
        "total_price": total_price,
        "order_token": token
    })

@login_required
def checkout_success_view(request):
    return render(request, "user_account/success.html")

# Subscriptions view
class SubscriptionPageView(TemplateView):
    template_name = 'user_account/subscriptions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plans = SubscriptionPlan.objects.all()
        context['plans'] = plans
        return context

