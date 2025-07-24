from django.urls import path
from . import views
from .views import profile_view, add_to_cart, cart_view

app_name = 'user_backend'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path("profile/", profile_view, name="profile"),
    path('logout/', views.logout_view, name='logout'),
    path('add-to-cart/<int:material_pk>/add_to_cart/', add_to_cart, name='add_to_cart'),
    path('cart', cart_view, name = 'cart'),
]