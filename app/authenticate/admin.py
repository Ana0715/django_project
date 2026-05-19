from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_active', 'is_company_owner', 'is_admin', 'date_joined')
    list_filter = ('is_active', 'is_company_owner', 'is_admin', 'date_joined')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('username',)}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_company_owner', 'is_admin')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_active', 'is_staff', 'is_company_owner', 'is_admin')}
        ),
    )

