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

    def update_details(self, detail, param):
        details = {detail: param}
        return TelegramUser.objects.filter(chat_id=self.chat_id).update(**details)


############################### shoud be reworked ####################################################
def session_initialize(user):
    return TelegramSession.objects.get_or_create(student=user, language=user.language, is_active=True)


def session_get(session_id):
    return TelegramSession.objects.get(pk=session_id)


def session_updater(user, detail, param):
    details = {detail: param}
    return TelegramSession.objects.filter(student=user, is_active=True).update(**details)
############################### shoud be reworked ####################################################


def _display_help(param=None):
    return render_to_string('tplatform/help.md')


def _display_roles(param=None):
    return render_to_string('tplatform/roles.md')


def _display_languages(param=None):
    return render_to_string('tplatform/languages.md')


def _display_details(param=None):
    return render_to_string('tplatform/details.md')


def _display_session(param=None):
    return render_to_string('tplatform/session.md')


def _display_details_changed(param=None):
    return "Grete, details has been changed. /status"


def _display_details_not_changed(param=None):
    return "Something went wrong, Please check your command. /details"


def _display_tutor_notice(user_info):
    return render_to_string('tplatform/tutor_notice.md').\
        format(name=user_info.student.name, language=user_info.language)


def _display_student_notice(user_info):
    return render_to_string('tplatform/student_notice.md'). \
        format(name=user_info.name, language=user_info.language)


def _display_status(user_info):
    return render_to_string('tplatform/status.md').\
        format(name=user_info.name, role=user_info.role, language=user_info.language)


def make_inline_keyboard(button_text_data):
    _button_set = []
    for text, data in button_text_data:
        _button_set.append([(InlineKeyboardButton(text=text, callback_data=data))])
    return InlineKeyboardMarkup(inline_keyboard=_button_set)


COMMANDS = {
            '/start':       (_display_help, None),
            '/help':        (_display_help, None),
            '/status':      (_display_status, None),
            '/role':        (_display_roles, make_inline_keyboard([('Student', 'student'),
                                                                  ('Tutor', 'tutor')])),
            '/language':    (_display_languages, make_inline_keyboard([('English', 'eng'),
                                                                      ('Russian', 'rus')])),
            '/session':     (_display_session, make_inline_keyboard([('Initialize', 'init'),
                                                                     ('Cancel', 'cancel')])),
            '/details':     (_display_details, None),

            # Commands which user are not allowed to be found
            '/details_has_been_changed':        (_display_details_changed, None),
            '/details_has_not_been_changed':    (_display_details_not_changed, None)
        }

# Callback for callbacks =)
EDIT_MESSAGE_TEXT = {
            '*tutor':                ("To start a session update your details /details", None),
            '*student':              ("To start a session choose language /language", None),
            '*init_success':         ("Session is initialized /session", None),
            '*init_invalid':         ("You already have an active session /session", None),
            '*cancel_success':       ("Session has been canceled /session", None),
            '*cancel_invalid':       ("You don't have an active session /session", None),
            '*connect':              ("You have been connect to session.\n"
                                      "Please wait while the student confirms session with you.", None),
            '*skip':                 ("Please wait next session", None),
            '*confirm':              ["To start session follow the link ", None],
            '*reject':               ("Please wait next tutor", None),

}


def _command_handler(cmd):
    _blank = dict()
    if cmd[0] == '/':
        _blank = COMMANDS
    elif cmd[0] == '*':
        _blank = EDIT_MESSAGE_TEXT
    result = _blank.get(cmd.lower(), None)
    return result


def flavor(msg):
    if isinstance(msg, dict):
        if 'callback_query' in msg:
            return 'callback_query'
        elif 'message' in msg:
            return 'chat'


def get_user_credential(msg, msg_type):
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


def notice_tutors(session):
    """
    Send notification to all tutors.
    Inline keyboard:
    Connect - contain session id.
    Skip - remove keyboard

    WARNING - should be added filter (notification on\off, language eng\rus)
    """
    tutor_list = TelegramUser.objects.filter(role='tutor')
    for tutor in tutor_list:
        TelePot.sendMessage(tutor.chat_id, _display_tutor_notice(session),
                            reply_markup=make_inline_keyboard(
                                [('Connect', 'connect {student_chat}'.format(student_chat=session.student.chat_id)),
                                 ('Skip', 'skip')]))


def notice_tutor(tutor):
    TelePot.sendMessage(tutor.chat_id, "The student has chosen you, please go to your channel {url}".
                        format(url=tutor.appear),)


def notice_student(student_chat, user):
    TelePot.sendMessage(student_chat, _display_student_notice(user),
                        reply_markup=make_inline_keyboard(
                            [('Confirm', 'confirm {tutor_appear}'.format(tutor_appear=user.chat_id)),
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
                    # command structure example index 0 [/details] index 1 [-phone] index 2 [+64-204-093-75-80]
                    # /details -phone +64-204-093-75-80
                text = message['message']['text']
                command = text.split(" ")
                if len(command) > 1 and command[0] == '/details':
                    if interlocutor.update_details(detail=command[1][1:], param=command[2]):
                        command[0] = '/details_has_been_changed'
                    else:
                        command[0] = '/details_has_not_been_changed'
                answer = _command_handler(cmd=command[0])
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
                    answer = "Sorry, I'm still learning, so I don't understand you \n" \
                             "Please check available commands /help"
                if isinstance(answer, str):
                    TelePot.sendMessage(chat_id, answer)
                else:
                    TelePot.sendMessage(chat_id, answer[0](_param), reply_markup=answer[1])

            elif message_type == 'callback_query':
                callback = (message['callback_query'])
                callback_answer = None
                answer = None
                _param = None
                if callback['data'] in ["student", 'tutor']:
                    if interlocutor.update_details(detail='role', param=callback['data']):
                        callback_answer = "Role is established: {role}".format(role=callback['data'])
                        answer = ("Role is established /language", None)
                    # if callback['data'] == 'tutor':
                    #     answer = _command_handler(cmd='tutor', blank=EDIT_MESSAGE_TEXT)
                    # elif callback['data'] == 'student':
                    #     answer = _command_handler(cmd='student', blank=EDIT_MESSAGE_TEXT)

                elif callback['data'] in ["eng", 'rus']:
                    if interlocutor.update_details(detail='language', param=callback['data']):
                        callback_answer = "Language is established: {language}".format(language=callback['data'])
                        answer = ("Language is established /session", None)
                elif callback['data'] in ['init', 'cancel']:
                    if callback['data'] == 'init':
                        session, is_created = session_initialize(user)
                        if is_created:
                            answer = _command_handler(cmd='*init_success')
                        else:
                            answer = _command_handler(cmd='*init_invalid')
                    if callback['data'] == 'cancel':
                        if session_updater(user, detail='is_active', param=False):
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
                        session_updater(user, detail='tutor', param=tutor)
                        session_updater(user, detail='is_going', param=True)
                    if callback['data'] == 'reject':
                        answer = _command_handler(cmd='*reject')
                TelePot.answerCallbackQuery(callback['id'], callback_answer)
                TelePot.editMessageText((telepot.message_identifier(msg=callback['message'])),
                                        answer[0], reply_markup=answer[1])
            return JsonResponse({}, status=200)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')

