from django import forms
from django.contrib.auth.models import User
from django.db.transaction import atomic
from library.models import Review, Rating
from user_account.models import UserProfile


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'content']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']

class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)


    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-white px-3 py-2'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-white px-3 py-2'
            }),
        }
        help_texts = {
            'username': None,
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance')
        initial = kwargs.get('initial', {})

        if user:
            try:
                profile = user.profile
                initial['full_name'] = profile.full_name
                initial['address'] = profile.address
            except UserProfile.DoesNotExist:
                pass
            kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

        self.fields['full_name'].widget.attrs.update({
            'class': 'w-full rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-white px-3 py-2'
        })
        self.fields['address'].widget.attrs.update({
            'class': 'w-full rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-white px-3 py-2'
        })
        

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.full_name = self.cleaned_data.get('full_name')
        profile.address = self.cleaned_data.get('address')
        if commit:
            profile.save()
        return user