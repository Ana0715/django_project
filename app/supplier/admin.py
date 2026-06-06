from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('title', 'inn', 'company')
    list_filter = ('company',)
    search_fields = ('title', 'inn',)
    readonly_fields = ('company', )

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'inn')
        }),
        ('Компания', {
            'fields': ('company',)
        }),
    )


