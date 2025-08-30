from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from user_account.models import CustomUser



class Category(models.Model):
    """
    Represents a category of reading materials, which may have a parent category, enabling hierarchical relationships.
    Attributes:
        name (str): The name of the category.
        parent (ForeignKey): A reference to the parent category. Null if it's a top-level category.
    Methods:
        __str__(): Returns the name of the category when the instance is printed or converted to a string.
    Meta:
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
    """
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='children', null=True, blank=True)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class Genre(models.Model):
    """
    Represents a genre of reading material, belonging to a specific category.
    Attributes:
        name (str): The name of the genre.
        category (ForeignKey): A reference to the category this genre belongs to.
    Methods:
        __str__(): Returns the name of the genre when the instance is printed or converted to a string.
    Meta:
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
    """
    name= models.CharField(max_length=255,verbose_name=_('Genre Name'), null=True, blank=True)
    category=models.ForeignKey(Category, on_delete= models.CASCADE, verbose_name='Category', related_name='genre', null=True, blank=True)

    class Meta:
        verbose_name=_('Genre')
        verbose_name_plural=_('Genres')

    def __str__(self):
        return self.name


class Author(models.Model):
    """
    Represents an author of reading materials, including their personal details and biography.
    Attributes:
        name (str): The author's first name.
        surname (str): The author's surname.
        date_of_birth (DateField): The author's date of birth.
        written_genres (str): A list of genres the author has written in.
        image (ImageField): The author's profile image.
        bio (TextField): A short biography of the author.
    Methods:
        __str__(): Returns the author's name when the instance is printed or converted to a string. If the name is not provided, "Unnamed Author" is returned.
    Meta:
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
    """
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
        return self.name or 'Unnamed Author'


class ReadingMaterials(models.Model):
    """
    Represents a reading material, such as a book, with information such as title, author, category, genre, price, and availability.
    Attributes:
        title (str): The title of the reading material.
        author (ForeignKey): The author of the reading material.
        category (ForeignKey): The category to which the material belongs.
        genre (ForeignKey): The genre of the material.
        book_summary (str): A brief description or summary of the material.
        release_date (DateField): The publication date of the material.
        price (DecimalField): The price of the reading material.
        image (ImageField): The cover image of the material.
        enabled (bool): A flag indicating whether the material is available for purchase.
        availability (bool): A flag indicating whether the material is in stock.
    Methods:
        __str__(): Returns the title of the reading material when the instance is printed or converted to a string. If the title is not provided, "Unnamed Material" is returned.
        average_rating(): Calculates and returns the average rating of the reading material based on all ratings.
        rating_distribution(): Returns a dictionary with the count of ratings for each star value (1 to 5).
    Meta:
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
    """
    title = models.CharField(max_length=255, verbose_name=_('Title'),  null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING, verbose_name=_('Author'), related_name='books', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name=_('Category'), null=True, blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, verbose_name=_('Genre'),  null=True, blank=True)
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
        return self.title or 'Unnamed Material'


class Review(models.Model):
    """
    Represents a review of a reading material written by a user.
    Attributes:
        book (ForeignKey): The reading material being reviewed.
        user (ForeignKey): The user who wrote the review.
        title (str): The title of the review.
        content (str): The content of the review.
    Methods:
        __str__(): Returns a string representation of the review, including the user and title of the review.

    Meta:
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
    """
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


class Rating(models.Model):
    """
    Represents a rating given by a user to a reading material.
    Attributes:
        book (ForeignKey): The reading material being rated.
        user (ForeignKey): The user who gave the rating.
        value (int): The rating value (1 to 5).
        created_at (datetime): The timestamp when the rating was created.
    Methods:
        __str__(): Returns a string representation of the rating, including the user, material, and rating value.
    Meta:
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
    """
    book = models.ForeignKey(ReadingMaterials, on_delete=models.CASCADE, verbose_name=_('Review'), related_name='ratings', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Rating')
        verbose_name_plural = _('Ratings')
        unique_together = ('book', 'user')

    def __str__(self):
        return f'{self.user} rated "{self.book}" {self.value} stars'


class SubscriptionPlan(models.Model):
    """
    Represents a subscription plan that offers specific benefits to users, such as price and duration.
    Attributes:
        name (str): The name of the subscription plan.
        price (DecimalField): The price of the subscription plan.
        duration_days (int): The duration of the subscription in days.
        description (str): A brief description of the subscription plan.
    Methods:
        __str__(): Returns a string representation of the subscription plan, including the plan name and duration in days.
    Meta:
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
    """
    name = models.CharField(max_length=100, verbose_name=_('Plan Name'), null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('Price'), null=True, blank=True)
    duration_days = models.PositiveIntegerField(verbose_name=_('Duration (days)'), null=True, blank=True)
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True,)

    class Meta:
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')

    def __str__(self):
        return f'{self.name} - {self.duration_days} days' if self.name else 'Unnamed Plan'

 
class Subscription(models.Model):
    """
    Represents a subscription made by a user to a specific subscription plan.
    Attributes:
        user (ForeignKey): The user who has made the subscription.
        plan (ForeignKey): The subscription plan that the user is subscribed to.
        start_date (datetime): The date when the subscription started.
        end_date (datetime): The date when the subscription ends (optional).
        active (bool): A flag indicating whether the subscription is active or not.
    Methods:
        __str__(): Returns a string representation of the subscription, including the user's email and the subscription plan's name.
    Meta:
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('User'), related_name='subscriptions', null=True, blank=True)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, verbose_name=_('Plan'), null=True, blank=True)
    start_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Start Date'))
    end_date = models.DateTimeField(verbose_name=_('End Date'), null=True, blank=True)
    active = models.BooleanField(default=True, verbose_name=_('Active'))

    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')

    def __str__(self):
        return f'{self.user.email} - {self.plan.name}' if self.user and self.plan else 'Incomplete Subscription'


class Order(models.Model):
    """
    Represents an order placed by a user for a reading material, containing payment and delivery details.
    Attributes:
        user (ForeignKey): The user who placed the order.
        total_cost (DecimalField): The total cost of the order.
        delivery_address (str): The delivery address for the order.
        user_address (str): The user’s address.
        submitted_at (datetime): The timestamp when the order was placed.
        client_full_name (str): The full name of the client placing the order.
        status (str): The status of the order (e.g., 'paid', 'pending', etc.).
        quantity (int): The quantity of items ordered.
        price_per_item (DecimalField): The price per item in the order.
        reading_material (ForeignKey): The reading material being ordered.
    Payment attributes:
        card_number (str): The credit card number used for the order (if applicable).
        card_expiry (str): The expiry date of the credit card (MM/YY format).
        card_cvv (str): The CVV code of the credit card.
        cardholder_name (str): The name of the cardholder.
        buy_session_hash (str): A unique hash representing the payment session.
    Methods:
        __str__(): Returns a string representation of the order, including the order ID and the title of the reading material.
        save(): Calculates and sets the total cost of the order before saving it to the database.
    Meta:
        verbose_name (str): The singular name for the model.
        verbose_name_plural (str): The plural name for the model.
    """
    class Status(models.TextChoices):
        PAID = 'paid', 'Paid'
        PENDING = 'pending', 'Pending'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    delivery_address = models.TextField(blank=True, null=True)
    user_address = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    client_full_name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    quantity = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    reading_material = models.ForeignKey(ReadingMaterials, on_delete=models.PROTECT, verbose_name=_('Reading Material'), null=True, blank=True)

    # Payment fields
    card_number = models.CharField(max_length=16, blank=True, null=True)
    card_expiry = models.CharField(max_length=5, blank=True, null=True)
    card_cvv = models.CharField(max_length=3, blank=True, null=True)
    cardholder_name = models.CharField(max_length=255, blank=True, null=True)
    buy_session_hash = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f'Order #{self.id} - {self.reading_material.title}'

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.price_per_item
        super().save(*args, **kwargs)
