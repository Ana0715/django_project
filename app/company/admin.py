from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'inn', 'owner')
    list_filter = ('inn',)
    search_fields = ('company_name', 'inn')
    readonly_fields = ('owner', )


    fieldsets = (
        ('Основная информация', {
            'fields': ('company_name', 'inn')
        }),
    )