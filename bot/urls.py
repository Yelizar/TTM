# -*- coding: utf8 -*-

from django.urls import path

from .views import CommandReceiveView

app_name = 'planet'

urlpatterns = [
     path('<path:bot_token>', CommandReceiveView.as_view(), name='command')

]
