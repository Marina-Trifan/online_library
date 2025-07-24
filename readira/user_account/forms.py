from django import forms
from django.db.transaction import atomic
from library.models import Review, Rating
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import CustomUser

CustomUser = get_user_model()

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'content']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'full_name',
            'avatar_url',
            'city',
            'country',
            'street',
            'zip_code',
            'preferred_channel',
            'email',
        ]
        widgets = {
            'preferred_channel': forms.Select(choices=CustomUser.Channel.choices),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    pass  # Can be customized further if needed