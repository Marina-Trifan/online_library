from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length = 255, verbose_name = _('Author'))
    date_of_birth = models.DateField(verbose_name=_('Date of Birth'), null=True)
    written_genres = models.CharField(max_length = 255, verbose_name=_('Genres'), null=True)
    bio = models.TextField(verbose_name = _('About the author'))

    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=255)

class BookType(models.Model):
    name = models.CharField(max_length=255)



class ReadingMaterials(models.Model):
    title = models.CharField(max_length = 255, verbose_name = _('Title'))
    author = models.ForeignKey(Author, on_delete = models.DO_NOTHING, verbose_name = _('Author'))
    genre = models.ForeignKey(Genre, on_delete = models.DO_NOTHING , verbose_name = _('Genre'))
    reading_material_type = models.ForeignKey(BookType, on_delete = models.DO_NOTHING , verbose_name = _('Type'))
    book_summary = models.TextField(verbose_name = _('Book Summary'))
    image = models.ImageField(upload_to = 'reading_materials/', verbose_name = _('Image'), null=True)
    enabled = models.BooleanField(default = True, verbose_name=('Enabled'))

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(rating.value for rating in ratings)/ratings.count(), 2)
        return 0

    def rating_distribution(self):
        return{
            i: self.ratings.filter(value = i).count()
            for i in range(1, 6)
        }
    
    class Meta:
        verbose_name = _('Reading material')
        verbose_name_plural = _('Reading Materials')

    def __str__(self):
        return self.title


class Review(models.Model):
    book = models.ForeignKey(ReadingMaterials, on_delete = models.CASCADE, related_name = 'reviews', verbose_name = _('Reading Material Review'))
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length = 255, verbose_name = _('Title'))
    content = models.TextField(verbose_name = _('Content'))

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        unique_together = ('book', 'user')


    def __str__(self):
        return f'User {self.user} left the review {self.title}: {self.content}'


class Rating(models.Model):
    book = models.ForeignKey(ReadingMaterials, related_name = 'ratings', on_delete = models.CASCADE, verbose_name = _('Review'))
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    value = models.IntegerField(validators = [MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name = _('Rating')
        verbose_name_plural = _('Ratings')
        unique_together = ('book', 'user')

    def __str__(self):
        return f'{self.user} rated "{self.book}" {self.value} stars'


# class ReadingMaterialsImage(models.Model):
#     reading_material = models.ForeignKey(ReadingMaterials, related_name = 'images', on_delete = models.CASCADE, verbose_name = _('Reading Material Image'))
#     image = models.ImageField(upload_to = 'reading_materials/', verbose_name = _('Image'))

    # class Meta:
    #     verbose_name = _('Reading Material Image')

    # def __str__(self):
    #     return f'{self.product.title} image.'






