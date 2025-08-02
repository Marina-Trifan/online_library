from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from user_account.models import CustomUser
from django.utils import timezone


# Category model:
class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

# Genre model:
class Genre(models.Model):
    name= models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Genre Name'))
    category=models.ForeignKey(Category, on_delete= models.CASCADE, related_name='genre', null=True, blank=True, verbose_name='Category')

    class Meta:
        verbose_name=_('Genre')
        verbose_name_plural=_('Genres')

    def __str__(self):
        return self.name

# Author model:
class Author(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Author'), null=True, blank=True)
    surname = models.CharField(max_length=255, verbose_name=_('Surname'), null=True, blank=True)
    date_of_birth = models.DateField(verbose_name=_('Date of Birth'), null=True, blank=True)
    written_genres = models.CharField(max_length=255, verbose_name=_('Genres'), null=True, blank=True)
    image = models.ImageField(upload_to='authors/', verbose_name=_('Image'), null=True, blank=True)
    bio = models.TextField(verbose_name=_('About the author'), null=True, blank=True)

    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')

    def __str__(self):
        return self.name or "Unnamed Author"

# Reading materials model:
class ReadingMaterials(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Title'))
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING, verbose_name=_('Author'), related_name='books', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name=_('Category'), null=True, blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Genre'))
    book_summary = models.TextField(verbose_name=_('Summary'), null=True, blank=True)
    release_date = models.DateField(verbose_name=_('Release Date'), null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    image = models.ImageField(upload_to='reading_materials/', verbose_name=_('Image'), null=True, blank=True)
    enabled = models.BooleanField(default=True, verbose_name=('Enabled'))
    availability = models.BooleanField(default=True)

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.value for r in ratings) / ratings.count(), 2)
        return 0

    def rating_distribution(self):
        return {i: self.ratings.filter(value=i).count() for i in range(1, 6)}

    class Meta:
        verbose_name = _('Reading material')
        verbose_name_plural = _('Reading Materials')

    def __str__(self):
        return self.title or "Unnamed Material"

# Review model:
class Review(models.Model):
    book = models.ForeignKey(ReadingMaterials, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('Reading Material Review'), null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name=_('Title'), null=True, blank=True)
    content = models.TextField(verbose_name=_('Content'), null=True, blank=True)

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        unique_together = ('book', 'user')

    def __str__(self):
        return f'Review by {self.user} - {self.title}'

# Rating model:
class Rating(models.Model):
    book = models.ForeignKey(ReadingMaterials, related_name='ratings', on_delete=models.CASCADE, verbose_name=_('Review'), null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Rating')
        verbose_name_plural = _('Ratings')
        unique_together = ('book', 'user')

    def __str__(self):
        return f'{self.user} rated "{self.book}" {self.value} stars'

# Subscription plan model:
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Plan Name'), null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('Price'), null=True, blank=True)
    duration_days = models.PositiveIntegerField(verbose_name=_('Duration (days)'), null=True, blank=True)
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))

    class Meta:
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')

    def __str__(self):
        return f"{self.name} - {self.duration_days} days" if self.name else "Unnamed Plan"

# Subscription model: 
class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions', verbose_name=_('User'), null=True, blank=True)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, verbose_name=_('Plan'), null=True, blank=True)
    start_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Start Date'))
    end_date = models.DateTimeField(verbose_name=_('End Date'), null=True, blank=True)
    active = models.BooleanField(default=True, verbose_name=_('Active'))

    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}" if self.user and self.plan else "Incomplete Subscription"

# Order model:
class Order(models.Model):
    class Status(models.TextChoices):
        PAID = 'paid', 'Paid'
        PENDING = 'pending', 'Pending'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'

    user = models.ForeignKey(CustomUser, related_name="orders", on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    delivery_address = models.TextField(blank=True, null=True)
    user_address = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    client_full_name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    quantity = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    reading_material = models.ForeignKey(ReadingMaterials, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Reading Material")

    # Payment fields
    card_number = models.CharField(max_length=16, blank=True, null=True)
    card_expiry = models.CharField(max_length=5, blank=True, null=True)  # Format: MM/YY
    card_cvv = models.CharField(max_length=3, blank=True, null=True)
    cardholder_name = models.CharField(max_length=255, blank=True, null=True)
    buy_session_hash = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.id} - {self.reading_material.title}"

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.price_per_item
        super().save(*args, **kwargs)
