import json
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import TelegramUser
from django.template.loader import render_to_string


TelePot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)


class Interlocutor:

    def __init__(self, message):
        self.name = message['message']['chat']['first_name']
        self.chat_id = message['message']['chat']['id']
        self.chat_type = message['message']['chat']['type']

    def is_authorized(self):
        user, is_created = TelegramUser.objects.get_or_create(
                chat_id=self.chat_id,
                name=self.name,
                chat_type=self.chat_type)
        return user, is_created

    def set_role(self, role):
        return TelegramUser.objects.get(chat_id=self.chat_id).update(role=role)


def _display_help():
    return render_to_string('tplatform/help.md')


def _send_roles():
    return render_to_string('tplatform/send_roles.md')


COMMANDS = {
            'start': _display_help,
            'help': _display_help,
            'role': _send_roles,
        }


def command_handler(cmd):
    result = COMMANDS.get(cmd.split()[0].lower())
    return result


@method_decorator(csrf_exempt, name='dispatch')
class TelegramBotView(View):
    """
    Handles a request from Telegram
    """
    @staticmethod
    def post(request, **kwargs):
        if kwargs['bot_token'] != settings.TELEGRAM_BOT_TOKEN:
            return HttpResponseForbidden('Invalid token')
        try:
            message = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')

        interlocutor = Interlocutor(message)
        user, is_created = interlocutor.is_authorized()

        command = message['message']['text']
        answer = command_handler(cmd=command)
        print(message)
        if is_created:
            TelePot.sendMessage(user.chat_id, 'Hi {username}'.format(username=user.username))
        if answer:
            keyboard = ReplyKeyboardMarkup(keyboard=[['Student', 'Tutor']])
            TelePot.sendMessage(user.chat_id, answer(), reply_markup=keyboard)
        else:
            TelePot.sendMessage(user.chat_id, 'Hi Body')

        return JsonResponse({}, status=200)
