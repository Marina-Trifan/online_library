from django.urls import path
from . import views
from .views import (
    profile_view,
    cart_view,
    SubscriptionPageView,
    StoreLoginView,
    RegisterView,
    choose_subscription,
    )

app_name = 'user_backend'

urlpatterns = [
    path("login/", StoreLoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", profile_view, name="profile"),
    path('logout/', views.logout_view, name='logout'),
    path('add-to-cart/<int:material_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:material_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', cart_view, name = 'cart'),
    path('checkout/<str:token>/', views.checkout_view, name='checkout'),
    path('checkout-success/', views.checkout_success_view, name='checkout_success'),
    path('subscriptions/', SubscriptionPageView.as_view(), name='subscriptions'),
    path('choose-plan/', choose_subscription, name='choose_plan'),
    path('cart/remove-subscription/', views.remove_subscription, name='remove_subscription'),
]