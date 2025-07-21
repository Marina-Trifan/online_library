from django.urls import path
from . import views


app_name='user_account'

urlpatterns = [
    path('login/', views.login_view, name='Login'),
    
]