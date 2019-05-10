from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, TutorDetails
from django.utils.translation import gettext, gettext_lazy as _


class TutorDetailsInline(admin.TabularInline):
    model = TutorDetails


class TutorDetailsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Details'), {'fields': ('phone_number', 'dob', 'cv', 'short_resume')}),
    )


class CustomUserAdmin(UserAdmin):

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'role')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'), # permissions, groups
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role')

    def get_inline_instances(self, request, obj=None):
        if obj.role == 'Tutor':
            inlines = [TutorDetailsInline]
            return [inline(self.model, self.admin_site) for inline in inlines]
        else:
            return [inline(self.model, self.admin_site) for inline in self.inlines]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(TutorDetails, TutorDetailsAdmin)






