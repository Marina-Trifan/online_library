from django.contrib import admin

from .models import Author, Genre, BookType, ReadingMaterials, Review, Rating, Subscription, SubscriptionPlan


# Register your models here.


admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(BookType)
admin.site.register(ReadingMaterials)
admin.site.register(Review)
admin.site.register(Rating)
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


