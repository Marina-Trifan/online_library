from django.contrib import admin

from .models import (
    Author, 
    ReadingMaterials,
    Genre, 
    Review, 
    Rating, 
    Subscription, 
    SubscriptionPlan,
    Category)


# Register your models here.


admin.site.register(Author)
admin.site.register(Review)
admin.site.register(Rating)

@admin.register(ReadingMaterials)
class ReadingMaterialsAdmin(admin.ModelAdmin):
    model=ReadingMaterials
    fields=['title', 'author', 'book_summary', 'release_date', 'price', 'image', 'availability', 'category', 'genre', 'enabled']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display=('name', 'category')
    list_filter=('category',)

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days')
    search_fields = ('name',)
    ordering = ('price',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'active')
    list_filter = ('active', 'plan')
    search_fields = ('user__username', 'user__email')


