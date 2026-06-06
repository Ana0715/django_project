from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'quantity', 'purchase_price', 'sale_price', 'storage')
    list_filter = ('storage__company',)
    search_fields = ('title',)
    readonly_fields = ('quantity', )

    fieldsets = (
        ('Информация о товаре', {
            'fields': ('title', 'purchase_price', 'sale_price')
        }),
        ('Склад', {
            'fields': ('storage',)
        }),
    )

