from django.contrib import admin
from .models import *


class LanguagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'language', 'is_active']
    list_display_links = ['language']

    search_fields = ['language']
    fields = ['language', 'is_active']


class CommunicationMethodsAdmin(admin.ModelAdmin):
    list_display = ['id', 'method', 'is_active']
    list_display_links = ['method']

    search_fields = ['method']
    fields = ['method', 'is_active']


class SessionCoinsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'coins', 'is_active', 'created', 'updated']
    list_display_links = ['user']

    search_fields = ['user']
    fields = ['user', 'coins', 'is_active']


class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'tutor', 'student_confirm', 'tutor_confirm', 'is_going']
    list_display_links = ['student', 'tutor']

    search_fields = ['student', 'tutor']
    fields = ['student', 'tutor', 'communication_method', 'student_confirm', 'tutor_confirm', 'is_going']

class ChannelRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'is_active']
    list_display_links = ['student']

    search_fields = ['student']
    fields = ['student', 'tutor']

admin.site.register(Languages, LanguagesAdmin)
admin.site.register(CommunicationMethods, CommunicationMethodsAdmin)
admin.site.register(SessionCoins, SessionCoinsAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(ChannelRoom, ChannelRoomAdmin)
