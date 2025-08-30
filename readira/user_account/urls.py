from django.urls import path
from .views import (
    StoreLoginView,
    RegisterView,
    SubscriptionPageView,
    profile_view,
    logout_view,
    add_to_cart,
    cart_view,
    remove_from_cart,
    checkout_view,
    checkout_success_view,
    choose_subscription,
    remove_subscription,
    )

app_name = 'user_account'

urlpatterns = [
    path('login/', StoreLoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
    path('add-to-cart/<int:material_id>/add_to_cart/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:material_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/', cart_view, name = 'cart'),
    path('checkout/<str:token>/', checkout_view, name='checkout'),
    path('checkout-success/', checkout_success_view, name='checkout_success'),
    path('subscriptions/', SubscriptionPageView.as_view(), name='subscriptions'),
    path('choose-plan/', choose_subscription, name='choose_plan'),
    path('cart/remove-subscription/', remove_subscription, name='remove_subscription'),
]