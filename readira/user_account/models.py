from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name=_('Profile'))
  full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Full Name'))
  city = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("City"))
  country = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Country"))
  street = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Street"))
  zip_code = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("ZIP Code"))
  avatar_url = models.URLField(null=True, blank=True, verbose_name=_("Avatar / Logo"))
  class Role(models.TextChoices):
    USER = "USER", _("User")
    ADMIN = "ADMIN", _("Admin")
  role = models.CharField(
    max_length=10,
    choices=Role.choices,
    default=Role.USER,
    verbose_name=_("Role"),
  )
  class Channel(models.TextChoices):
    EMAIL = "email", _("Email")
    MAIL = "mail", _("Postal Mail")
  preferred_channel = models.CharField(
    max_length=10,
    choices=Channel.choices,
    default=Channel.EMAIL,
    verbose_name=_("Preferred Communication Channel"),
  )
  def __str__(self):
    return f"Profile of {self.user.username}"

