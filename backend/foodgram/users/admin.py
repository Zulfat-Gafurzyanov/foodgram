from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'avatar')}),
    )
    list_display = ('username', 'id', 'email', 'first_name', 'last_name',)
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')
