from django.contrib import admin

from .models import Author, Genre, BookType, ReadingMaterials, Review, Rating


# Register your models here.


admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(BookType)
admin.site.register(ReadingMaterials)
admin.site.register(Review)
admin.site.register(Rating)

