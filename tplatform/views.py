import json
import telepot
import types
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


def _display_roles(param=None):
    return render_to_string('tplatform/roles.md')


def _display_languages(param=None):
    return render_to_string('tplatform/languages.md')


def _display_details(param=None):
    return render_to_string('tplatform/details.md')


def _display_notifications(notice):
    if notice is None:
        notice = 'OFF'
    return render_to_string('tplatform/notifications.md').format(status=notice)


def _display_session(param=None):
    return render_to_string('tplatform/session.md')


def _display_details_changed(param=None):
    return "Grete, details has been changed. /status"


def _display_details_not_changed(param=None):
    return "Something went wrong, Please check your command. /details"


def _display_notification_changed(notice):
    if notice == 'on':
        answer = "Grete, You are able to receive notifications."
    else:
        answer = "Hope you see soon."
    return answer + "\n Notification: {notice}".format(notice=notice)


def _display_notification_not_changed(param=None):
    return "Something went wrong, Please check your command. /notifications "


def _display_tutor_notice(user_info):
    return render_to_string('tplatform/tutor_notice.md').\
        format(name=user_info.student.name, language=user_info.language)


def _display_student_notice(user_info):
    return render_to_string('tplatform/student_notice.md'). \
        format(name=user_info.name, language=user_info.language)


def _display_status(user_info):
    return render_to_string('tplatform/status.md').\
        format(name=user_info.name, role=user_info.role, language=user_info.language)


def _display_sorry(param=None):
    return "Sorry, I'm still learning, so I don't understand you \n" \
                             "Please check available commands /help"


def _display_not_allowed(role):
    return 'This command is not available to {role}'.format(role=role)


def _display_role_assigned(role):
    return "Role assigned. To change role contact to administrator. Your role is {role}".format(role=role)


def make_inline_keyboard(button_text_data):
    """
    :param button_text_data: list. [0] - Name of button [1] - Data of button
    :return: replay_markup(inline keyboard)
    """
    _button_set = []
    for text, data in button_text_data:
        _button_set.append([(InlineKeyboardButton(text=text, callback_data=data))])
    return InlineKeyboardMarkup(inline_keyboard=_button_set)


COMMANDS = {
            '/start':               (_display_help, None, None),
            '/help':                (_display_help, None, None),
            '/status':              (_display_status, None, None),
            '/role':                (_display_roles, make_inline_keyboard([('Student', 'student'),
                                                                  ('Tutor', 'tutor')]), None),
            '/language':            (_display_languages, make_inline_keyboard([('English', 'eng'),
                                                                      ('Russian', 'rus')]), None),
            '/session':             (_display_session, make_inline_keyboard([('Initialize', 'init'),
                                                                     ('Cancel', 'cancel')]), 'student'),
            '/details':             (_display_details, None, 'tutor'),
            '/notifications':       (_display_notifications, make_inline_keyboard([('ON', 'on'),
                                                                     ('OFF', 'off')]), 'tutor'),

            # Commands which user are not allowed to be found
            '/_whaaaat?':                            (_display_sorry, None, None),
            '/_command_not_allowed':                 (_display_not_allowed, None, None),
            '/_role_assigned':                       (_display_role_assigned, None, None),
            '/_details_has_been_changed':            (_display_details_changed, None, 'tutor'),
            '/_details_has_not_been_changed':        (_display_details_not_changed, None, 'tutor'),
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
            '*_notification_has_been_changed':       (_display_notification_changed, None),
            '*_notification_has_not_been_changed':   (_display_notification_not_changed, None)

}


def _access_check(pattern, role):
    """
    :param pattern: str. 'student' or 'tutor' only
    :param role: str. Telegram.object.role
    :return: bool
    """
    return True if pattern is None or pattern == role else False


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
    tutor_list = TelegramUser.objects.filter(role='tutor', notice=True, language=session.language)
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
                _param = None
                if is_created:
                    TelePot.sendMessage(user.chat_id, 'Hi {username}'.format(username=user.name))
                    # command structure example index 0 [/details] index 1 [-phone] index 2 [+64-204-093-75-80]
                    # /details -phone +64-204-093-75-80
                text = message['message']['text']
                command = text.split()
                answer = _command_handler(cmd=command[0])
                if answer:
                    if _access_check(pattern=answer[-1], role=user.role):
                        if len(command) > 1:
                            _internal_command = None
                            detail = command[1][1:].lower()
                            if command[0] == '/details':
                                if interlocutor.update_details(details={detail: command[2]}):
                                    _internal_command = '/_details_has_been_changed'
                                else:
                                    _internal_command = '/_details_has_not_been_changed'
                            if _internal_command is None:
                                answer = '/_whaaaat?'
                            else:
                                answer = _command_handler(cmd=_internal_command)
                        # Display Status
                        elif answer[0].__name__ == '_display_status':
                            _param = user
                        # Display Roles
                        elif answer[0].__name__ == '_send_roles':
                            if user.role is not None:
                                answer = '/_role_assigned'
                                _param = user.role
                        # Display Notification
                        elif answer[0].__name__ == '_display_notifications':
                            notice = _notice_handler(boolean=user.notice)
                            _param = notice
                    else:
                        answer = '/_command_not_allowed'
                        _param = user.role
                # Display if Command is not recognized
                else:
                    answer = '/_whaaaat?'
                if isinstance(answer, str):
                    answer = _command_handler(cmd=answer)
                TelePot.sendMessage(chat_id, answer[0](_param), reply_markup=answer[1])

            elif message_type == 'callback_query':
                callback = (message['callback_query'])
                callback_answer = None
                answer = None
                _param = None
                if callback['data'] in ["student", 'tutor']:
                    if interlocutor.update_details(details={'role': callback['data']}):
                        callback_answer = "Role is established: {role}".format(role=callback['data'])
                        answer = ("Role is established /language", None)
                    # if callback['data'] == 'tutor':
                    #     answer = _command_handler(cmd='tutor')
                    # elif callback['data'] == 'student':
                    #     answer = _command_handler(cmd='student')
                elif callback['data'] in ["eng", 'rus']:
                    if interlocutor.update_details(details={'language': callback['data']}):
                        callback_answer = "Language is established: {language}".format(language=callback['data'])
                        if user.role == 'student':
                            answer = _command_handler("*student")
                        elif user.role == 'tutor':
                            answer = _command_handler("*tutor")
                        else:
                            answer = _command_handler(cmd='*role')
                elif callback['data'] in ['init', 'cancel']:
                    if callback['data'] == 'init':
                        session, is_created = session_initialize(user)
                        if is_created:
                            answer = _command_handler(cmd='*init_success')
                        else:
                            answer = _command_handler(cmd='*init_invalid')
                    if callback['data'] == 'cancel':
                        if session_updater(user, details={'is_active': False}):
                            answer = _command_handler(cmd='*cancel_success')
                        else:
                            answer = _command_handler(cmd='*cancel_invalid')
                elif callback['data'] in ['connect', 'skip'] or 'connect' in callback['data']:
                    if 'connect' in callback['data']:
                        student_chat_id = callback['data'].split(" ")[1]
                        notice_student(student_chat=student_chat_id, user=user)
                        answer = _command_handler(cmd='*connect')
                    if callback['data'] == 'skip':
                        answer = _command_handler(cmd='*skip')
                elif callback['data'] in ['confirm', 'reject'] or 'confirm' in callback['data']:
                    if 'confirm' in callback['data']:
                        tutor_chat_id = callback['data'].split(" ")[1]
                        tutor = TelegramUser.objects.get(chat_id=tutor_chat_id)
                        answer = _command_handler(cmd='*confirm')
                        answer[0] += " {url}".format(url=tutor.appear)
                        notice_tutor(tutor=tutor)
                        session_updater(user, details={'tutor': tutor, 'is_going': True})
                    if callback['data'] == 'reject':
                        answer = _command_handler(cmd='*reject')
                elif callback['data'] in ['on', 'off']:
                    notice = _notice_handler(switcher=callback['data'])
                    if interlocutor.update_details(details={'notice': notice}):
                        answer = _command_handler(cmd='*_notification_has_been_changed')
                        _param = callback['data']
                    else:
                        answer = _command_handler(cmd='*_notification_has_not_been_changed')
                        _param = user.notice

                TelePot.answerCallbackQuery(callback['id'], callback_answer)
                if isinstance(answer[0], types.FunctionType):
                    TelePot.editMessageText((telepot.message_identifier(msg=callback['message'])),
                                            answer[0](_param), reply_markup=answer[1])
                else:
                    TelePot.editMessageText((telepot.message_identifier(msg=callback['message'])),
                                            answer[0], reply_markup=answer[1])
            return JsonResponse({}, status=200)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')

