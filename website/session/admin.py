from django.contrib import admin
from .models import *


class SessionCoinsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'coins', 'is_active', 'created', 'updated']
    list_display_links = ['user']

    search_fields = ['user']
    fields = ['user', 'coins', 'is_active']


class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'tutor', 'student_confirm', 'tutor_confirm', 'is_going']
    list_display_links = ['student', 'tutor']

    search_fields = ['student', 'tutor']
    fields = ['student', 'tutor', 'student_confirm', 'tutor_confirm', 'is_going']


class ChannelRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'is_active']
    list_display_links = ['student']

    search_fields = ['student']
    fields = ['student', 'tutor']


admin.site.register(SessionCoins, SessionCoinsAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(ChannelRoom, ChannelRoomAdmin)
