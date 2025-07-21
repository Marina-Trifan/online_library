from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.transaction import atomic
from library.models import Review, Rating
from user_account.models import UserProfile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required = True, label = 'Email address')
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name', 'email']
    
    @atomic
    def save(self, commit=True):
        self.instance.is_active = False
        result = super().save(commit)
        profile = Profile(user = result)

        if commit:
            profile.save()
        return result

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'content']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']