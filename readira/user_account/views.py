import hashlib
from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views import View
from django.views.decorators.http import require_POST, require_http_methods
from django.views.generic import TemplateView
from .forms import CustomPasswordChangeForm, CustomUserForm, EmailLoginForm
from library.models import ReadingMaterials, SubscriptionPlan, Subscription, Order


User = get_user_model()


class StoreLoginView(LoginView):
    """
    Login view for the store that uses a custom EmailLoginForm for authentication.
    Redirects users to choose a subscription plan if they have not completed their first login, otherwise redirects to the main page.
    Methods:
        - get_success_url(): Determines the URL to redirect to after a successful login.
                            Returns:
                                str: URL to subscription plan selection or main page.
    """
    template_name = 'user_account/login.html'
    authentication_form = EmailLoginForm

    def get_success_url(self):
        user = self.request.user
        if not user.first_login_complete:
            return reverse_lazy('user_account:choose_plan')
        return reverse_lazy('library:main_page')



class RegisterView(View):
    """
    User registration view handling GET and POST requests.
    Methods:
        - get(): Handles GET requests to show the registration page.
                Args:
                    request (HttpRequest): The HTTP request.
                Returns:
                    HttpResponse: Rendered registration page.
        - post(): Handles POST requests to create a new user.
                  Validates password confirmation and uniqueness of the email before creation.
                Args:
                    request (HttpRequest): The HTTP request containing form data.
                Returns:
                    HttpResponseRedirect or HttpResponse: Redirects to cart on success, or re-renders form with errors.
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('user_account:profile')
        email = request.GET.get('email', '')
        return render(request, 'user_account/register.html', {'email': email})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('user_account:profile')

        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        context = {'email': email}

        if password != confirm_password:
            context['error'] = 'Passwords do not match.'
            return render(request, 'user_account/register.html', context)

        if User.objects.filter(email=email).exists():
            context['error'] = 'Email already registered.'
            return render(request, 'user_account/register.html', context)

        user = User.objects.create_user(email=email, password=password)
        login(request, user)
        return redirect('user_account:login')


@login_required
def profile_view(request):
    """
    Displays and handles updates to the user's profile and password.
    Supports POST requests to update profile details or change password.
    Shows user subscriptions, orders, and other profile info.
    Args:
        request (HttpRequest): The HTTP request.
    Returns:
        HttpResponse: Rendered profile page with forms and data.
    """
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

    subs = user.subscriptions.all().order_by('active', '-start_date') if hasattr(user, 'subscriptions') else []
    orders = user.orders.all().order_by('-submitted_at') if hasattr(user, 'orders') else []
    has_sub = user.has_active_subscription
    fields = ['full_name', 'phone', 'city', 'country', 'street', 'zip_code', 'avatar_url', 'preferred_channel']

    return render(request, 'user_account/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'orders': orders,
        'subscriptions': subs,
        'has_subscription': has_sub,
        'fields': fields
    })



class SubscriptionPageView(TemplateView):
    """
    Displays the subscriptions page with a list of all available subscription plans.
    Methods: 
        - get_context_data(): Extends context data by adding all subscription plans.
                            Args:
                                **kwargs: Additional keyword arguments.
                            Returns:
                            dict: Context data including all subscription plans.
    """
    template_name = 'user_account/subscriptions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plans = SubscriptionPlan.objects.all()
        context['plans'] = plans
        return context


@login_required
def logout_view(request):
    """
    Logs out the current user and redirects to the homepage.
    Args:
        request (HttpRequest): The HTTP request.
    Returns:
        HttpResponseRedirect: Redirect to homepage.
    """
    logout(request)
    return redirect('/')



@login_required
def add_to_cart(request, material_id):
    """
    Adds a reading material to the user's cart stored in session.
    If the item is already in the cart, increments its quantity.
    Creates an order token for checkout if it doesn't exist.
    Args:
        request (HttpRequest): The HTTP request containing POST data.
        material_id (int): ID of the reading material to add.
    Returns:
        HttpResponseRedirect: Redirect to the cart page.
    """
    material = get_object_or_404(ReadingMaterials, id=material_id)
    quantity = int(request.POST.get('quantity', 1))

    cart = request.session.get('cart', {})
    key = str(material.id)

    if key in cart:
        cart[key]['quantity'] += quantity
        cart[key]['total'] = round(cart[key]['quantity'] * float(cart[key]['price']), 2)
    else:
        cart[key] = {
            'material_id': material.id,
            'title': material.title,
            'thumbnail': material.image.url if material.image else '',
            'price': float(material.price or 0),
            'quantity': quantity,
            'total': round(float(material.price or 0) * quantity, 2),
        }  

    # Ensure token is created only once
    if 'order_token' not in request.session:
        raw = f'{request.user.id}-{get_random_string(12)}'
        token = hashlib.sha256(raw.encode()).hexdigest()
        request.session['order_token'] = token

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('user_account:cart')



@login_required
def cart_view(request):
    """
    Displays the user's cart contents, total price, selected subscription plan, and order token.
    Supports selecting a subscription plan which adds to the cart total.
    Args:
        request (HttpRequest): The HTTP request.
    Returns:
        HttpResponse: Rendered cart page with context data.
    """
    cart = request.session.get('cart', {})
    materials = []
    total = Decimal('0.0')

    plan_id = request.GET.get('plan_id')
    if plan_id:
        try:
            plan = SubscriptionPlan.objects.get(pk=plan_id)
            request.session['selected_plan_id'] = plan.id
            request.session.modified = True
        except SubscriptionPlan.DoesNotExist:
            pass
    selected_plan = None
    stored_plan_id = request.session.get('selected_plan_id')
    if stored_plan_id:
        try:
            selected_plan = SubscriptionPlan.objects.get(pk=stored_plan_id)
        except SubscriptionPlan.DoesNotExist:
            request.session.pop('selected_plan_id', None)
    has_active_subscription = False
    if selected_plan:
        has_active_subscription = Subscription.objects.filter(
            user=request.user,
            plan=selected_plan,
            end_date__gte=timezone.now(),
            active=True
        ).exists()

    for item in cart.values():
        try:
            material = ReadingMaterials.objects.get(pk=item['material_id'])
            material.quantity = item['quantity']
            material.total = item['total']
            materials.append(material)
            total += Decimal(str(material.total))
        except ReadingMaterials.DoesNotExist:
            continue
    if selected_plan:
        total += selected_plan.price  

    if 'order_token' not in request.session:
        raw = f'{request.user.id}-{get_random_string(12)}'
        token = hashlib.sha256(raw.encode()).hexdigest()
        request.session['order_token'] = token

    order_token = request.session.get('order_token')
    return render(request, 'user_account/cart.html', {
        'materials': materials,
        'total_price': total,
        'order_token': order_token,
        'selected_plan':selected_plan,
        'has_active_subscription': has_active_subscription,
    })



@require_POST
def remove_from_cart(request, material_id):
    """
    Removes a reading material from the cart stored in session.
    Args:
        request (HttpRequest): The HTTP request.
        material_id (int): ID of the reading material to remove.
    Returns:
        HttpResponseRedirect: Redirect to the cart page.
    """
    cart = request.session.get('cart', {})
    material_key = str(material_id)
    if material_key in cart:
        del cart[material_key]
        request.session.modified = True
    return redirect('user_account:cart')


@login_required
def choose_subscription(request):
    """
    Allows a user to choose whether to subscribe or skip subscription on first login.
    GET:
        - Displays the choice page if the user has not completed their first login flow.
    POST:
        - Saves user's choice and marks first login as complete.
        - Redirects to subscription plans page or reading materials page based on choice.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: Redirects or renders the subscription choice template.
    """
    user = request.user
    if user.first_login_complete:
        return redirect('library:reading_materials')
    if request.method =='POST':
        choice = request.POST.get('choice')
        user.first_login_complete = True
        user.save()
        if choice =='subscribe':
            return redirect('user_account:subscriptions')
        else:
            return redirect('library:reading_materials')
    return render(request, 'user_account/choose_plan.html')


@require_POST
@login_required
def remove_subscription(request):
    """
    Removes the selected subscription plan from the session cart.
    Args:
        request (HttpRequest): The HTTP request.
    Returns:
        HttpResponseRedirect: Redirect to the cart page.
    """
    if 'selected_plan_id' in request.session:
        del request.session['selected_plan_id']
        request.session.modified = True
        messages.success(request, 'Subscription plan removed from your cart.')
    return redirect('user_account:cart')



@require_http_methods(['GET', 'POST'])
@login_required
def checkout_view(request, token):
    """
    Handles the checkout process for the user. Supports both GET and POST requests.
    GET:
        - Displays the checkout page with the total price and order token.
        - Validates the existence of cart items or selected subscription plan.
        - Validates the session token against the token parameter.
    POST:
        - Validates credit card details submitted by the user.
        - Creates Order entries for each item in the cart.
        - Creates a Subscription if a plan is selected and no active subscription exists.
        - Clears the cart, token, and selected plan from the session upon successful checkout.
    Args:
        request (HttpRequest): The HTTP request object.
        token (str): The unique order token to verify the checkout session.
    Returns:
        HttpResponse: Redirects to cart on errors or checkout success page after completion.
    """
    cart = request.session.get('cart', {})
    session_token = request.session.get('order_token')

    if (not cart and not request.session.get('selected_plan_id')) or session_token != token:
        messages.error(request, 'Invalid or expired checkout session.')
        return redirect('user_account:cart')

    total_price = sum(item['total'] for item in cart.values())

    selected_plan = None
    plan_id = request.session.get('selected_plan_id')
    if plan_id:
        try:
            selected_plan = SubscriptionPlan.objects.get(pk=plan_id)
            total_price += selected_plan.price
        except SubscriptionPlan.DoesNotExist:
            request.session.pop('selected_plan_id', None)

    if selected_plan:
        existing_active = Subscription.objects.filter(
            user=request.user,
            plan=selected_plan,
            end_date__gte=timezone.now(),
            active=True
        ).exists()
        if existing_active:
            messages.error(request, 'You already have an active subscription for this plan.')
            return redirect('user_account:cart')

    if request.method == 'POST':
        # Validate fields
        cardholder_name = request.POST.get('cardholder_name', '').strip()
        card_number = request.POST.get('card_number', '').strip()
        card_expiry = request.POST.get('card_expiry', '').strip()
        card_cvv = request.POST.get('card_cvv', '').strip()
        errors = []

        if not card_number.isdigit() or len(card_number) != 16:
            errors.append('Card number must be exactly 16 digits.')
        if len(cardholder_name.split()) < 2:
            errors.append('Cardholder name must contain at least two names.')
        if not card_expiry or len(card_expiry) != 5 or card_expiry[2] != '/':
            errors.append('Expiration date must be in MM/YY format.')
        else:
            try:
                month, year = map(int, card_expiry.split('/'))
                expiry_date = datetime.strptime(f'{month}/20{year}', '%m/%Y')
                if expiry_date < datetime.now().replace(day=1):
                    errors.append('Card expiry must be in the future.')
            except ValueError:
                errors.append('Invalid expiration date format.')
        if not card_cvv.isdigit() or len(card_cvv) != 3:
            errors.append('CVV must be exactly 3 digits.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'user_account/checkout.html', {
                'total_price': total_price,
                'order_token': token,
                'selected_plan': selected_plan,
            })

        # Create orders
        for item in cart.values():
            Order.objects.create(
                user=request.user,
                client_full_name=cardholder_name,
                delivery_address=request.user.street,
                user_address=request.user.city,
                reading_material=ReadingMaterials.objects.get(id=item['material_id']),
                quantity=item['quantity'],
                price_per_item=item['price'],
                card_number=card_number,
                card_expiry=card_expiry,
                card_cvv=card_cvv,
                cardholder_name=cardholder_name,
                buy_session_hash=hashlib.sha256(
                    f'{card_number}{card_expiry}{cardholder_name}{get_random_string(8)}'.encode()
                ).hexdigest(),
                status=Order.Status.PAID,
            )

        # Create subscription only if one isn't active for the same plan
        if selected_plan:
            from django.utils.timezone import now
            from datetime import timedelta

            existing_active = Subscription.objects.filter(
                user=request.user,
                plan=selected_plan,
                end_date__gte=now(),
                active=True
            ).exists()

            if not existing_active:
                start_date = timezone.now()
                end_date = start_date + timedelta(days=selected_plan.duration_days or 30)

                Subscription.objects.create(
                    user=request.user,
                    plan=selected_plan,
                    start_date=start_date,
                    end_date=end_date,
                    active=True
                )

        # Finalize: clear cart + token
        request.session.pop('cart', None)
        request.session.pop('order_token', None)
        request.session.pop('selected_plan_id', None)
        request.session.modified = True

        return redirect('user_account:checkout_success')

    return render(request, 'user_account/checkout.html', {
        'total_price': total_price,
        'order_token': token
    })

@login_required
def checkout_success_view(request):
    """
    Displays a confirmation page after a successful checkout.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: Renders the success page template.
    """
    return render(request, 'user_account/success.html')
