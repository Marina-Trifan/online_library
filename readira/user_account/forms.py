from django import forms
from django.db.transaction import atomic
from library.models import Review, Rating
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


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
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_passord')
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_('Incorrect password.'), code='password_incorrect')
        return old_password



class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            "id": "email",
            "class": "w-full px-4 py-2 rounded-xl border border-gray-400 text-black",
            "required": "required",
        })
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            "id": "password",
            "class": "w-full px-4 py-2 rounded-xl border border-gray-400 text-black",
            "required": "required",
        })
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        if email and password:
            self.user = authenticate(self.request, username=email, password=password)
            if self.user is None:
                raise forms.ValidationError(_("Invalid email or password."))
            elif not self.user.is_active:
                raise forms.ValidationError(_("This account is inactive."))
        return self.cleaned_data

    def get_user(self):
        return self.user