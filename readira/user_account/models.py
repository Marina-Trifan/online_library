from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'profile', verbose_name=_('User'))
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Full Name'))
    address = models.TextField(blank=True, null=True, verbose_name=_('Address'))

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name=_('User Profile')
        verbose_name_plural=_('User Profiles')

