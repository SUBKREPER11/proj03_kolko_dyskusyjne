from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'email_verified', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'email_verified')
    fieldsets = UserAdmin.fieldsets + (
        ('Kolko dyskusyjne', {'fields': ('email_verified', 'avatar', 'bio', 'theme')}),
    )
