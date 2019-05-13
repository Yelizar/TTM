from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, TutorDetails, TutorStatus
from django.utils.translation import gettext, gettext_lazy as _


class TutorDetailsInline(admin.TabularInline):
    model = TutorDetails


class TutorStatusInline(admin.TabularInline):
    model = TutorStatus


class TutorDetailsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Details'), {'fields': ('phone_number', 'dob', 'cv', 'short_resume', 'is_active')}),
    )
    list_display = ('user', 'is_active',)


class TutorStatusAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('user',)}),
        (None, {'fields': ('is_active',)}),
    )
    list_display = ('user', 'is_active',)


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'role')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),  # permissions, groups
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role', 'is_online')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role', 'is_online')

    def get_inline_instances(self, request, obj=None):
        if obj.role == 'Tutor':
            inlines = [TutorDetailsInline, TutorStatusInline]
            return [inline(self.model, self.admin_site) for inline in inlines]
        else:
            return [inline(self.model, self.admin_site) for inline in self.inlines]


admin.site.register(TutorStatus, TutorStatusAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(TutorDetails, TutorDetailsAdmin)
