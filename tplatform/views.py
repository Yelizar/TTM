import json
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import TelegramUser
from django.template.loader import render_to_string
import pprint


TelePot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)


class Interlocutor:

    def __init__(self, name=None, chat_id=None, chat_type=None):
        self.name = name
        self.chat_id = chat_id
        self.chat_type = chat_type

    def is_authorized(self):
        return TelegramUser.objects.get_or_create(
                chat_id=self.chat_id,
                name=self.name,
                chat_type=self.chat_type)

    def set_role(self, role):
        return TelegramUser.objects.get(chat_id=self.chat_id).update(role=role)


def _display_help():
    return render_to_string('tplatform/help.md')


def _send_roles():
    return render_to_string('tplatform/send_roles.md')


COMMANDS = {
            '/start': (_display_help, None),
            '/help': (_display_help, None),
            '/role': (_send_roles,
                      InlineKeyboardMarkup(inline_keyboard=[
                          [InlineKeyboardButton(text='Student', callback_data='student')],
                          [InlineKeyboardButton(text='Tutor', callback_data='tutor')]
                      ])),
        }


def command_handler(cmd):
    result = COMMANDS.get(cmd.split()[0].lower())
    return result


def flavor(msg):
    if isinstance(msg, dict):
        if 'callback_query' in msg:
            return 'callback_query'
        elif 'message' in msg:
            return 'chat'


def get_user_credential(msg, msg_type):
    """
    Recognize user credential in msg.
    :param msg:
    :param msg_type:
    :return: object Interlocutor()
    """
    if msg_type == 'chat':
        if 'chat' in msg['message']:
            _chat = msg['message']['chat']
            name = _chat['first_name']
            chat_id = _chat['id']
            chat_type = _chat['type']
            return name, chat_id, chat_type
    elif msg_type == 'callback_query':
        if 'from' in msg['callback_query']:
            _from = msg['callback_query']['from']
            name = _from['first_name']
            chat_id = _from['id']
            return name, chat_id, None


@method_decorator(csrf_exempt, name='dispatch')
class TelegramBotView(View):
    """
    Handles a request from Telegram
    """
    @staticmethod
    def post(request, **kwargs):
        if kwargs['bot_token'] != settings.TELEGRAM_BOT_TOKEN:
            return HttpResponseForbidden('Invalid token')
        request_body = request.body.decode('utf-8')
        try:
            message = json.loads(request_body)
            message_type = flavor(message)
            pprint.pprint(message)
            first_name, chat_id, chat_type = get_user_credential(msg=message, msg_type=message_type)
            interlocutor = Interlocutor(name=first_name, chat_id=chat_id, chat_type=chat_type)
            user, is_created = interlocutor.is_authorized()
            if message_type == 'chat':
                if is_created:
                    TelePot.sendMessage(user.chat_id, 'Hi {username}'.format(username=user.username))
            else:
                print(message['callback_query']['data'])
                TelePot.answerCallbackQuery(message['callback_query']['id'], 'Now you are {role}'.format(role=message['callback_query']['data']))
                interlocutor.set_role(role=message['callback_query']['data'])
                return JsonResponse({}, status=200)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')

        command = message['message']['text']
        answer = command_handler(cmd=command)
        if answer:
            TelePot.sendMessage(user.chat_id, answer[0](), reply_markup=answer[1])
        else:
            TelePot.sendMessage(user.chat_id, 'Hi Body')

        return JsonResponse({}, status=200)
