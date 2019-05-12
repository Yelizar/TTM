# -*- coding: utf8 -*-

import json
import logging

import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

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

def _display_help(chat_id):

    handlers = {
        UserRole.USER_ADMIN: 'talktome/admin.md',
        UserRole.USER_NEWB: 'talktome/hello.md',
        UserRole.USER_LEARNER: 'talktome/learner.md',
        UserRole.USER_TUTOR: 'talktome/tutor.md',
    }

    if not chat_id in Users:
        new_user = {
            'nativeLang' : LanguageSet.LANG_UNKNOWN,
            'communicationLang' : LanguageSet.LANG_ENG,
            'role' : UserRole.USER_NEWB,
            'bannedByAdmin' : False,
        }

        Users[chat_id] = new_user

    role = Users[chat_id]['role']


    file_name = handlers.get(role)
    return render_to_string(file_name)

def _display_planetpy_feed(chat_id):
    return render_to_string('py_planet/feed.md', {'items': parse_planetpy_rss()})

def _learner_register(chat_id):
    Users[chat_id]['role'] = UserRole.USER_LEARNER
    return render_to_string('talktome/learner.md')

def _tutor_register(chat_id):
    Users[chat_id]['role'] = UserRole.USER_TUTOR
    return render_to_string('talktome/tutor.md')

def _admin_dump(chat_id):
    with open('talktome.users.json', mode='w', encoding='utf-8') as f:
        json.dump(Users, f, indent=2)
    return "Saved {} users' items".format(len(Users))

def _admin_load(chat_id):
    with open('talktome.users.json', mode='r', encoding='utf-8') as f:
        Users = json.load(f)
    return "Loaded {} users' items".format(len(Users))

class CommandReceiveView(View):
    def post(self, request, bot_token):
        print(bot_token or "None")
        if bot_token != settings.TELEGRAM_BOT_TOKEN:
            return HttpResponseForbidden('Invalid token')

        commands = {
            '/start': _display_help,
            '/help': _display_help,
            '/learner': _learner_register,
            '/tutor': _tutor_register,
            '/dump': _admin_dump,
            '/load': _admin_load,
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
