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
  address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
  city = forms.CharField(required=False)
  country = forms.CharField(required=False)
  street = forms.CharField(required=False)
  zip_code = forms.CharField(required=False)
  avatar_url = forms.URLField(required=False, label="Avatar (Image URL)")
  preferred_channel = forms.ChoiceField(choices=UserProfile.Channel.choices, required=False)
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
        initial.update({
          'full_name': getattr(profile, 'full_name', ''),
          'address': getattr(profile, 'address', ''),
          'city': profile.city,
          'country': profile.country,
          'street': profile.street,
          'zip_code': profile.zip_code,
          'avatar_url': profile.avatar_url,
          'preferred_channel': profile.preferred_channel,
        })
      except UserProfile.DoesNotExist:
        pass
      kwargs['initial'] = initial
    super().__init__(*args, **kwargs)
    # Optional: Add styling to the new fields
    for field in self.fields.values():
      field.widget.attrs.update({
        'class': 'w-full rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-white px-3 py-2'
      })
  def save(self, commit=True):
    user = super().save(commit=commit)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.full_name = self.cleaned_data.get('full_name')
    profile.address = self.cleaned_data.get('address')
    profile.city = self.cleaned_data.get('city')
    profile.country = self.cleaned_data.get('country')
    profile.street = self.cleaned_data.get('street')
    profile.zip_code = self.cleaned_data.get('zip_code')
    profile.avatar_url = self.cleaned_data.get('avatar_url')
    profile.preferred_channel = self.cleaned_data.get('preferred_channel')
    if commit:
      profile.save()
    return user