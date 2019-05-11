# -*- coding: utf8 -*-

import json
import logging

import telepot
from telebot import types

from django.template.loader import render_to_string
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from .utils import parse_planetpy_rss


TelegramBot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)

logger = logging.getLogger('telegram.bot')


class LanguageSet(object):
    LANG_UNKNOWN = 0
    LANG_ENG = 1
    LANG_RUS = 2
    LANG_OTHER = 3

class UserRole(object):
    USER_ADMIN = 0
    USER_NEWB = 1
    USER_LEARNER = 2
    USER_TUTOR = 3

Users = {}

class User(object):
    def __init__(self):
        self.nativeLang = LanguageSet.LANG_UNKNOWN
        self.communicationLang = LanguageSet.LANG_ENG
        self.role = UserRole.USER_NEWB
        self.bannedByAdmin = False


def _display_help(chat_id):

    handlers = {
        UserRole.USER_ADMIN: 'talktome/admin.md',
        UserRole.USER_NEWB: 'talktome/help.md',
        UserRole.USER_LEARNER: 'talktome/learner.md',
        UserRole.USER_TUTOR: 'talktome/tutor.md',
    }

    if chat_id in Users:
        markup = None
        role = Users[chat_id].role
    else:
        markup = types.ReplyKeyboardMarkup()
        markup.row("Leaner", "Tutor")
        role = UserRole.USER_NEWB

    file_name = handlers.get(role)
    message = render_to_string(file_name)
    TelegramBot.sendMessage(chat_id, message, parse_mode='Markdown', reply_markup=markup)

def _display_planetpy_feed(chat_id):
    message = render_to_string('py_planet/feed.md', {'items': parse_planetpy_rss()})
    TelegramBot.sendMessage(chat_id, message, parse_mode='Markdown')


class CommandReceiveView(View):
    def post(self, request, bot_token):
        print(bot_token or "None")
        if bot_token != settings.TELEGRAM_BOT_TOKEN:
            return HttpResponseForbidden('Invalid token')

        commands = {
            '/start': _display_help,
            '/help': _display_help,
            'feed': _display_planetpy_feed,
        }

        raw = request.body.decode('utf-8')
        logger.info(raw)

        try:
            payload = json.loads(raw)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            chat_id = payload['message']['chat']['id']
            cmd = payload['message'].get('text')  # command

            func = commands.get(cmd.split()[0].lower())
            if func:
                TelegramBot.sendMessage(chat_id, func(chat_id), parse_mode='Markdown')
            else:
                TelegramBot.sendMessage(chat_id, 'I do not understand you, Sir!')

        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)
