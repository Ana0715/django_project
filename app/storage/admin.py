from django.contrib import admin
from .models import Storage


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('address', 'company')
    list_filter = ('company',)
    search_fields = ('address',)

    fieldsets = (
        ('Информация о складе', {
            'fields': ('address', 'company')
        }),
    )