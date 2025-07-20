from django import forms
from django.contrib.auth.forms import UserCreationForm
from library.models import Review, Rating


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'content']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']