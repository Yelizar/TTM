# -*- coding: utf8 -*-

from django.urls import path
import tplatform.views as view

app_name = 'tplatform'

urlpatterns = [
     path('<path:bot_token>', view.TelegramBotView.as_view(), name='command')

]
