# -*- coding: utf8 -*-

import telepot

from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from .talktome.agency import talktome as ttm


TelegramBot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)


class CommandReceiveView(View):
    def post(self, request, bot_token):
        print(bot_token or "None")
        if bot_token != settings.TELEGRAM_BOT_TOKEN:
            return HttpResponseForbidden('Invalid token')

        try:
            chat_id, message = ttm.process(request)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            TelegramBot.sendMessage(chat_id, message, parse_mode='Markdown')

        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)
