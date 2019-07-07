import json
import telepot
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import TelegramUser, TelegramSession
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
import pprint


TelePot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)


class Interlocutor:
    """
    Contains main info about telegram user
    """

    def __init__(self, name=None, chat_id=None, chat_type=None):
        self.name = name
        self.chat_id = chat_id
        self.chat_type = chat_type

    def is_authorized(self):
        return TelegramUser.objects.get_or_create(
                chat_id=self.chat_id,
                name=self.name,
                chat_type=self.chat_type)

    def update_details(self, details):
        print(details)
        try:
            return TelegramUser.objects.filter(chat_id=self.chat_id).update(**details)
        except ValidationError:
            return False


def session_initialize(user):
    """
    :param user: class TelegramUser()
    :return: class TelegramSession and True if created() False if get()
    """
    return TelegramSession.objects.get_or_create(student=user, language=user.language, is_active=True)


def session_get(session_id):
    """
    :param session_id: int.
    :return:
    """
    return TelegramSession.objects.get(pk=session_id)


def session_updater(user, details):
    """
    :param user: class TelegramUser()
    :param details: dict. {field: value}
    :return: True or False
    """
    return TelegramSession.objects.filter(student=user, is_active=True).update(**details)


def _display_help(param=None):
    return render_to_string('tplatform/help.md')


def _display_sorry(param=None):
    return "Sorry, I'm still learning, so I don't understand you \n" \
                             "Please check available commands /help"


def _display_tutor_notice(user_info):
    return render_to_string('tplatform/tutor_notice.md').\
        format(name=user_info.student.name, language=user_info.language)


def _display_student_notice(user_info):
    return render_to_string('tplatform/student_notice.md'). \
        format(name=user_info.name, language=user_info.language)


def make_inline_keyboard(button_text_data, back=None):
    """
    :param button_text_data: list. [0] - Name of button [1] - Data of button
    :return: replay_markup(inline keyboard)
    """
    _button_set = []
    _page = 0
    for text, data in button_text_data:
        _button_set.append([(InlineKeyboardButton(text=text, callback_data=data))])
    if back:
        print(back)
        _button_set.insert(0, [(InlineKeyboardButton(text='Back', callback_data=back))])
        _button_set.append([(InlineKeyboardButton(text='On Top', callback_data='on_top'))])
    return InlineKeyboardMarkup(inline_keyboard=_button_set)


COMMANDS = {
            '/start':               (None, [('Placement', '*placement'),
                                                     ('TalkToMe', '*talk_to_me'),
                                                     ('TeachForUs', '*teach_for_us')]),
            '/help':                (_display_help, [('Placement', '*placement'),
                                                     ('TalkToMe', '*talk_to_me'),
                                                     ('TeachForUs', '*teach_for_us')]),

            # Command which user are not allowed to be found
            '/_whaaaat?':                            (_display_sorry, None),
        }

# Callback for callbacks =)
EDIT_MESSAGE_TEXT = {
            '*role':                 ("Please set up your role /role", None),
            '*tutor':                ("To receive notifications please update your details /details", None),
            '*student':              ("To begin a session click here /session", None),
            '*init_success':         ("Session is initialized /session", None),
            '*init_invalid':         ("You already have an active session /session", None),
            '*cancel_success':       ("Session has been canceled /session", None),
            '*cancel_invalid':       ("You don't have an active session /session", None),
            '*connect':              ("You have been connect to session.\n"
                                      "Please wait while the student confirms session with you.", None),
            '*skip':                 ("Please wait next session", None),
            '*confirm':              ["To start session follow the link ", None],
            '*reject':               ("Please wait next tutor", None),

            '*talk_to_me':              (None, [('Settings', '*s_settings'),
                                                ('Session', '*s_session')]),
            '*s_settings':              (None, [('Native Language', '*native_language'),
                                                ('Learning Language', '*learning_language')]),
            '*native_language':         (None, [('English', '_eng'),
                                                ('Russian', '_rus')]),
            '*learning_language':       (None, [('English', '_eng'),
                                                ('Russian', '_rus')]),

            '*s_session':               (None, [('Initialize', '_init_session'),
                                                ('Cancel', '_cancel_session'),
                                                ('History', '_history_session')]),
            '*teach_for_us':            (None, [('Settings', '*t_settings'),
                                                ('Session', '*t_session')]),

            '*t_settings':              (None, [('Appear', '_appear'),
                                                ('Phone', '_phone')]),


}


def _notice_handler(boolean=None, switcher=None):
    """
    Function performs the role to switch True to 'ON' False to 'OFF'
    :param boolean: True or False
    :param switcher: 'on' or 'off'
    :return: bool or str
    """
    if boolean:
        return 'ON' if boolean is True else 'OFF'
    elif switcher:
        return True if switcher == 'on' else False


def _command_handler(cmd):
    """
    :param cmd: str. It's a command(/) or internal command to change message(*) or text message (from user)
    :return: tuple or None . It contains 3 params.
    result[0] - function() which return always str
    result[1] - None or InlineKeyboardMarkup()
    result[2] - None or str 'tutor'/'student' to check access a user to a command
    """
    _blank = dict()
    if cmd[0] == '/':
        _blank = COMMANDS
    elif cmd[0] == '*':
        _blank = EDIT_MESSAGE_TEXT
    result = _blank.get(cmd.lower(), None)
    return result


def flavor(msg):
    """
    :param msg: dict - received from telegram user(unserialized data JSON -> dict)
    :return: str - message type.
    A message's flavor may be one of these:

    - ``chat``
    - ``callback_query``
    - ``edited_message``
    - ``unrecognized``
    planned- ``inline_query``
    planned- ``chosen_inline_result``
    planned- ``shipping_query``
    planned- ``pre_checkout_query``
    """
    if isinstance(msg, dict):
        if 'callback_query' in msg:
            return 'callback_query'
        elif 'message' in msg:
            return 'chat'
        elif 'edited_message' in msg:
            return 'edited_message'
        else:
            return 'unrecognized'


def get_user_credential(msg, msg_type):
    """
    :param msg: dict - received from telegram user(unserialized data JSON -> dict)
    :param msg_type: read return: of flavor(msg)
    :return:
    """
    _chat = None
    if msg_type == 'chat':
        if 'chat' in msg['message']:
            _chat = msg['message']['chat']
    elif msg_type == 'callback_query':
        if 'chat' in msg['callback_query']['message']:
            _chat = msg['callback_query']['message']['chat']
    elif msg_type == 'edited_message':
        if 'chat' in msg['edited_message']:
            _chat = msg['edited_message']['chat']
    ###################### should be rewoked #########################
    elif msg_type == 'unrecognized':
        return None, None, None
    ##################################################################
    name = _chat['first_name']
    chat_id = _chat['id']
    chat_type = _chat['type']
    return name, chat_id, chat_type


def notice_tutors(session):
    """
    :param session: class. TelegramSession()
    Send notification to all tutors(Notification - ON, Language = Student.language)
    Inline keyboard:
    Connect - contain session id.
    Skip - remove keyboard
    """
    tutor_list = TelegramUser.objects.filter(notice=True, language=session.language)
    for tutor in tutor_list:
        TelePot.sendMessage(tutor.chat_id, _display_tutor_notice(session),
                            reply_markup=make_inline_keyboard(
                                [('Connect', 'connect {student_chat}'.format(student_chat=session.student.chat_id)),
                                 ('Skip', 'skip')]))


def notice_tutor(tutor):
    """
    :param tutor: class TelegramUser()
    Send notification to a tutor who has been chosen by student
    """
    TelePot.sendMessage(tutor.chat_id, "The student has chosen you, please go to your channel {url}".
                        format(url=tutor.appear),)


def notice_student(student_chat, user):
    """
    :param student_chat: str TelegramUser.object.chat_id
    :param user: class TelegramUser(). Tutor instance who has been sent your details to student
    :return:
    Send notification to a student from tutor.
    """
    TelePot.sendMessage(student_chat, _display_student_notice(user),
                        reply_markup=make_inline_keyboard(
                            [('Confirm', 'confirm {chat_id}'.format(chat_id=user.chat_id)),
                             ('Reject', 'reject')]))


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
                text = message['message']['text']
                command = text.split()
                answer = _command_handler(cmd=command[0])
                if answer is None:
                    answer = _command_handler(cmd='/_whaaaat?')
                TelePot.sendMessage(chat_id, answer[0](), reply_markup=make_inline_keyboard(answer[1]))

            elif message_type == 'callback_query':
                callback = (message['callback_query'])
                root = callback['message']['reply_markup']['inline_keyboard'][0][0]['callback_data']
                answer = None
                _param = None
                data = callback['data']
                if data[0] == '*':
                    answer = _command_handler(cmd=data)
                elif 'back_to' in data:
                    back = data.split('#')
                    answer = _command_handler(cmd=back[-2])
                    del back[-1]
                    root = '#'.join(back)
                elif data == 'on_top':
                    answer = _command_handler(cmd='/start')
                    root = 'back_to #/start'
                elif data in ["eng", 'rus']:
                    if interlocutor.update_details(details={'language': data}):
                        callback_answer = "Language is established: {language}".format(language=data)
                        if user.role == 'student':
                            answer = _command_handler("*student")
                        elif user.role == 'tutor':
                            answer = _command_handler("*tutor")
                        else:
                            answer = _command_handler(cmd='*role')
                        TelePot.answerCallbackQuery(callback['id'], callback_answer)
                elif data in ['_init_session', '_cancel_session']:
                    if data == '_init_session':
                        session, is_created = session_initialize(user)
                        if is_created:
                            answer = _command_handler(cmd='*init_success')
                        else:
                            answer = _command_handler(cmd='*init_invalid')
                    if data == '_cancel_session':
                        if session_updater(user, details={'is_active': False}):
                            answer = _command_handler(cmd='*cancel_success')
                        else:
                            answer = _command_handler(cmd='*cancel_invalid')
                elif data in ['connect', 'skip'] or 'connect' in data:
                    if 'connect' in data:
                        student_chat_id = data.split(" ")[1]
                        notice_student(student_chat=student_chat_id, user=user)
                        answer = _command_handler(cmd='*connect')
                    if data == 'skip':
                        answer = _command_handler(cmd='*skip')
                elif data in ['confirm', 'reject'] or 'confirm' in data:
                    if 'confirm' in data:
                        tutor_chat_id = data.split(" ")[1]
                        tutor = TelegramUser.objects.get(chat_id=tutor_chat_id)
                        answer = _command_handler(cmd='*confirm')
                        answer[0] += " {url}".format(url=tutor.appear)
                        notice_tutor(tutor=tutor)
                        session_updater(user, details={'tutor': tutor, 'is_going': True})
                    if data == 'reject':
                        answer = _command_handler(cmd='*reject')
                elif data in ['on', 'off']:
                    notice = _notice_handler(switcher=data)
                    if interlocutor.update_details(details={'notice': notice}):
                        answer = _command_handler(cmd='*_notification_has_been_changed')
                        _param = data
                    else:
                        answer = _command_handler(cmd='*_notification_has_not_been_changed')
                        _param = user.notice
                replay_markup = None
                if root == '*placement':
                    _back = 'back_to #/start#{line}'.format(line=data)
                elif root == 'back_to #/start':
                    _back = None
                elif len(root) < len(data):
                    _back = root
                else:
                    _back = root + '#{line}'.format(line=data)
                if answer[1]:
                    replay_markup = make_inline_keyboard(button_text_data=answer[1], back=_back)
                if answer[0] is None:
                    TelePot.editMessageReplyMarkup(telepot.message_identifier(msg=callback['message']),
                                                   reply_markup=replay_markup)
                else:
                    TelePot.editMessageText((telepot.message_identifier(msg=callback['message'])),
                                            answer[0], reply_markup=replay_markup)
            return JsonResponse({}, status=200)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')

