from django.contrib import admin
from .models import Supply, SupplyProduct


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'delivery_date')
    list_filter = ('delivery_date', 'supplier__company')
    search_fields = ('supplier__title',)
    readonly_fields = ('delivery_date', )

    def has_change_permission(self, request, obj=None):
        return False # Запрет редактирования

    def has_delete_permission(self, request, obj=None):
        return False # Запрет удаления

@admin.register(SupplyProduct)
class SupplyProductAdmin(admin.ModelAdmin):
    list_display = ('supply', 'product', 'quantity')
    list_filter = ('supply__delivery_date', )
    readonly_fields = ('supply', 'product', 'quantity',)
    
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

