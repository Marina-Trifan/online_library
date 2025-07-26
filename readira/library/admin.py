from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Author, 
    ReadingMaterials,
    Genre, 
    Review, 
    Rating, 
    Subscription, 
    SubscriptionPlan,
    Category, Order)


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

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client_full_name',
        'reading_material',
        'quantity',
        'price_per_item',
        'total_cost',
        'status',
        'submitted_at',
    )
    list_filter = ('status', 'submitted_at')
    search_fields = ('client_full_name', 'product_title', 'user__email')
    readonly_fields = ('submitted_at', 'total_cost', 'buy_session_hash')

    fieldsets = (
        (_('Order Details'), {
            'fields': (
                'user',
                'client_full_name',
                'reading_material',
                'quantity',
                'price_per_item',
                'total_cost',
                'status',
            )
        }),
        (_('Addresses'), {
            'fields': ('user_address', 'delivery_address'),
        }),
        (_('Card Info'), {
            'fields': (
                'cardholder_name',
                'card_number',
                'card_expiry',
                'card_cvv',
                'buy_session_hash',
            )
        }),
        (_('Meta'), {
            'fields': ('submitted_at',),
        }),
    )


