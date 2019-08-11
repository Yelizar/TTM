# -*- coding: utf8 -*-

from django.urls import path
from .views import TelegramBotView

app_name = 'tplatform'

urlpatterns = [
     path('<path:bot_token>', TelegramBotView.as_view(), name='command')

]
