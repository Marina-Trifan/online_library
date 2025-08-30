from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _



class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser model that handles user creation.
    Methods:
        - create_user(): Creates and saves a regular user with the given email and password.
                        Args:
                            email (str): The user's email address, used as username.
                            password (str, optional): The user's password.
                            **extra_fields: Additional fields to set on the user model.
                        Raises:
                            ValueError: If email is not provided.
                        Returns:
                            CustomUser: The newly created user instance.
        - create_superuser(): Creates and saves a superuser with the given email and password.
                            Args:
                                email (str): The superuser's email address.
                                password (str): The superuser's password.
                                **extra_fields: Additional fields to set on the superuser model.
                            Returns:
                                CustomUser: The newly created superuser instance.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)



class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model extending AbstractBaseUser and PermissionsMixin.
    Fields:
        email (EmailField): Unique email used for authentication.
        city (CharField): User's city (optional).
        country (CharField): User's country (optional).
        street (CharField): User's street address (optional).
        zip_code (CharField): User's postal code (optional).
        avatar_url (URLField): URL to user's avatar or logo (optional).
        full_name (CharField): User's full name.
        phone (CharField): User's phone number.
        role (CharField): User's role, choices are ADMIN or USER.
        preferred_channel (CharField): Preferred communication channel.
        is_active (BooleanField): Designates whether this user is active.
        is_staff (BooleanField): Designates whether user can access admin site.
        first_login_complete (BooleanField): Tracks if user has completed first login.
    Properties:
        has_active_subscription (bool): Returns True if user has an active subscription.
    Managers:
        objects: CustomUserManager instance.
    Methods:
        - has_active_subscription(): Checks if the user currently has an active subscription.
                                    Returns: bool: True if the user has at least one active subscription with an end date in the future or today, False otherwise.
        - __str__(): Returns the string representation of the user.
                    Returns:
                        str: The user's email address. 
    Meta:
        verbose_name: "User"
        verbose_name_plural: "Users"
    """
    email = models.EmailField(unique=True, verbose_name=_('Email (Login)'))
    city = models.CharField(max_length=100, verbose_name=_('City'), null=True, blank = True)
    country = models.CharField(max_length=100, verbose_name=_('Country'), null=True, blank = True)
    street = models.CharField(max_length=255, verbose_name=_('Street'), null=True, blank = True)
    zip_code = models.CharField(max_length=20, verbose_name=_('ZIP Code'), null=True, blank = True)

    avatar_url = models.URLField(verbose_name=_('Avatar / Logo / Thumbnail'), null=True, blank=True)
    full_name = models.CharField(max_length=150, verbose_name=_('Full Name'), blank=True)
    phone = models.CharField(max_length=30, verbose_name=_('Phone'), blank=True)

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        USER = 'USER', _('User')

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER, verbose_name=_('Role'))

    class Channel(models.TextChoices):
        EMAIL = 'email', _('Email')
        MAIL = 'mail', _('Postal Mail')

    preferred_channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.EMAIL, verbose_name=_('Preferred Communication Channel'))

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    first_login_complete = models.BooleanField(default=False, verbose_name=_('First login complete'))

    objects = CustomUserManager()

    @property
    def has_active_subscription(self):
        from django.utils.timezone import now
        return self.subscriptions.filter(active=True, end_date__gte=now()).exists()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email