import json
import telepot
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
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
        return TelegramUser.objects.filter(chat_id=self.chat_id).update(role=role)


def _display_help(param=None):
    return render_to_string('tplatform/help.md')


def _send_roles(param=None):
    return render_to_string('tplatform/send_roles.md')


def _display_status(user_info):
    return "Name: {name} \nRole: {role} \nMore Info...".format(name=user_info.name, role=user_info.role)


COMMANDS = {
            '/start':       (_display_help, None),
            '/help':        (_display_help, None),
            '/status':      (_display_status, None),
            '/role':        (_send_roles,
                             InlineKeyboardMarkup(inline_keyboard=[
                                 [InlineKeyboardButton(text='Student', callback_data='student')],
                                 [InlineKeyboardButton(text='Tutor', callback_data='tutor')]
                              ])),
        }


def _command_handler(cmd):
    result = COMMANDS.get(cmd.lower())
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
    _chat = None
    if msg_type == 'chat':
        if 'chat' in msg['message']:
            _chat = msg['message']['chat']
    elif msg_type == 'callback_query':
        if 'chat' in msg['callback_query']['message']:
            _chat = msg['callback_query']['message']['chat']
    name = _chat['first_name']
    chat_id = _chat['id']
    chat_type = _chat['type']
    return name, chat_id, chat_type


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

            pprint.pprint(message)  # Print to check request

            first_name, chat_id, chat_type = get_user_credential(msg=message, msg_type=message_type)
            interlocutor = Interlocutor(name=first_name, chat_id=chat_id, chat_type=chat_type)
            user, is_created = interlocutor.is_authorized()
            if message_type == 'chat':
                if is_created:
                    TelePot.sendMessage(user.chat_id, 'Hi {username}'.format(username=user.name))
            elif message_type == 'callback_query':
                callback = (message['callback_query'])
                TelePot.answerCallbackQuery(message['callback_query']['id'],
                                            'Now you are {role}'.format(role=message['callback_query']['data']))
                interlocutor.set_role(role=callback['data'])
                TelePot.editMessageReplyMarkup((telepot.message_identifier(msg=callback['message'])))
                return JsonResponse({}, status=200)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        command = message['message']['text']
        answer = _command_handler(cmd=command)
        _param = None
        # Display Status
        if answer and answer[0].__name__ == '_display_status':
            _param = user
        # Display Roles
        elif answer and answer[0].__name__ == '_send_roles':
            if user.role is not None:
                answer = "You are already {role}".format(role=user.role)
        # Display if Command is not recognized
        elif answer is None:
            answer = "Sorry, I'm still learning, so I don't understand you \n"\
                     "Please check available commands /help"
        if isinstance(answer, str):
            TelePot.sendMessage(chat_id, answer)
        else:
            TelePot.sendMessage(chat_id, answer[0](_param), reply_markup=answer[1])

        return JsonResponse({}, status=200)
