from django.contrib import admin
from .models import Sale, ProductSale


class ProductSaleInline(admin.TabularInline):
    model = ProductSale
    extra = 0
    readonly_fields = ('product', 'quantity')
    can_delete = False  # нельзя менять/удалять товары из админки


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer_name', 'sale_date', 'company')
    list_filter = ('company', 'sale_date')
    search_fields = ('buyer_name', 'company__company_name')
    readonly_fields = ('company', )
    inlines = [ProductSaleInline]


@admin.register(ProductSale)
class ProductSaleAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity',)
    list_filter = ('sale__company', 'sale__sale_date')
    readonly_fields = ('sale', 'product')

