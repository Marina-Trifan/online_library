from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _
from library.models import Review, Rating
from .models import CustomUser


CustomUser = get_user_model()


class ReviewForm(forms.ModelForm):
    """
    Form for submitting a review for a reading material.
    Meta fields:
        - title: The title of the review.
        - content: The content/body of the review.
    """
    class Meta:
        model = Review
        fields = ['title', 'content']



class RatingForm(forms.ModelForm):
    """
    Form for submitting a numeric rating (1 to 5) for a reading material.
    Meta fields:
        - value: Integer rating value.
    """
    class Meta:
        model = Rating
        fields = ['value']


class CustomUserForm(forms.ModelForm):
    """
    Form for editing custom user profile information.
    Meta fields:
        - full_name
        - avatar_url
        - city
        - country
        - street
        - zip_code
        - preferred_channel
        - email
    """
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
    """
    Custom password change form with validation for old password.
    Methods:
        - clean_old_password(): Validates that the old password is correct.
                                        Raises:
                                            ValidationError: If the old password is incorrect.
                                        Returns:
                                            str: The validated old password.
    """
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_passord')
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_('Incorrect password.'), code='password_incorrect')
        return old_password



class EmailLoginForm(forms.Form):
    """
    Form for logging in users via email and password.
    Meta Fields:
        - email: The user's email address.
        - password: The user's password.
    Mthods:
        - clean(): Validates the user credentials using Django's authentication system.
                        Raises:
                            ValidationError: If the credentials are invalid or the account is inactive.
                        Returns:
                            dict: Cleaned data after validation.
        - get_user(): Returns the authenticated user object.
                            Returns:
                                CustomUser or None

    """

    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'id': 'email',
            'class': 'w-full px-4 py-2 rounded-xl border border-gray-400 text-black',
            'required': 'required',
        })
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'id': 'password',
            'class': 'w-full px-4 py-2 rounded-xl border border-gray-400 text-black',
            'required': 'required',
        })
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user = authenticate(self.request, username=email, password=password)
            if self.user is None:
                raise forms.ValidationError(_('Invalid email or password.'))
            elif not self.user.is_active:
                raise forms.ValidationError(_('This account is inactive.'))
        return self.cleaned_data

    def get_user(self):
        return self.user