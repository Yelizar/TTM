from django.contrib import admin
from .models import *
from django.utils.translation import gettext_lazy as _


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'role', 'is_active']
    list_display_links = ['username']
    list_filter = ['role']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )

    class Meta:
        model = User


admin.site.register(User, UserAdmin)
