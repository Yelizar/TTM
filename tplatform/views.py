import json
import os
import pprint
import types

import telepot
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from django.db.models import Q

from tplatform.models import TelegramUser, TelegramSession, TelegramTest
from tplatform.utilit import add_questions, HELLO_STRING


def _notice_handler(data):
    """
    Function performs the role to switch True to 'ON' False to 'OFF'
    :return: bool or str
    """
    if isinstance(data, bool):
        return 'ON' if data is True else 'OFF'
    else:
        return True if data == 'on' else False


def user_level(score):
    """Checking user level"""
    level = ""
    if 0 <= score <= 15:
        level = "Starter"
    if 15 < score <= 35:
        level = "Elementary"
    if 35 < score <= 55:
        level = "Pre-Intermediate"
    if 55 < score <= 75:
        level = "Intermediate"
    if 75 < score <= 95:
        level = "Upper Intermediate"
    if score > 95:
        level = "Advanced"
    return level


def _display_help():
    return render_to_string('tplatform/help.md')


def _display_sorry():
    return "Sorry, I'm still learning, so I don't understand you \n" \
                             "Please check available commands /help"


def _display_details_updated():
    return "Details Updated.\nOpen new menu /start"


COMMANDS = {
            '/start':               (_display_help, (('Placement', '*placement'),
                                                     ('TalkToMe', '*talk_to_me'),
                                                     ('TeachForUs', '*teach_for_us'))),
            '/help':                (_display_help, (('Placement', '*placement'),
                                                     ('TalkToMe', '*talk_to_me'),
                                                     ('TeachForUs', '*teach_for_us'))),
            # '/s_confirm_session':       (_display_session_confirm, (('Excellent', '_session_excellent'),
            #                                     ('Nice', '_session_nice'),
            #                                     ('Terrible', '_session_terrible'),
            #                                     ('Canceled', '_s_session_canceled'))),
            # '/t_confirm_session':       (_display_session_confirm, (('Done', '_session_done'),
            #                                     ('Canceled', '_t_session_canceled'))),
            # '/history_session':      (_display_history_session, None),
            # '/check_result':         (_display_test_result, None),
            # Command which user are not allowed to be found
            '/_details_updated':                      (_display_details_updated, None),
            '/_whaaaat?':                            (_display_sorry, None),
        }

# Callback for callbacks =)
EDIT_MESSAGE_TEXT = {
    """
    #########################
    #   *   |    Folder     #
    #       |               #
    #   _   |    Commands   #
    #       |               #
    #   #   |    Divider    #
    #       |               #
    # await |Wait an answer #
    #########################
    """     '*connect':              ("You have been connect to session.\n"
                                      "Please wait while the student confirms session with you.", None),
            '*skip':                 ("Please wait next session", None),
            # '*confirm':              ["To start session follow the link ", None],
            '*reject':               ("Please wait next tutor", None),

            '*root':                    (None, (('Placement', '*placement'),
                                                ('TalkToMe', '*talk_to_me'),
                                                ('TeachForUs', '*teach_for_us'))),

            '*talk_to_me':              (None, (('Settings', '*s_settings'),
                                                ('Session', '*s_session'))),
            '*s_settings':              (None, (('Native Language', '*native_language'),
                                                ('Learning Language', '*learning_language'))),
            '*native_language':         ['Choose your native language', (('English', '_native_language#eng'),
                                                ('Russian', '_native_language#rus'))],
            '*learning_language':       ['Choose learning language', (('English', '_learning_language#eng'),
                                                ('Russian', '_learning_language#rus'))],

            '*s_session':               [None, None, ((('Initialize', '_init_session'),
                                                        ('Cancel', '_cancel_session'),
                                                       ('History', '/history_session')),
                                                        {'session': ('is_active', True)})],
            '*teach_for_us':            [None, None, ((('Apply', '_apply'),
                                                      ('Notification', '*notification'),
                                                        ('Settings', '*t_settings')),
                                                        {'user': ('is_active', False)})],
            '*notification':            [None, None, ((('On', '_notice_on'),
                                                      ('Off', '_notice_off')),
                                                        {'user': ('notice', False)})],

            '*t_settings':              [None, (('Appear', '_appear#await'),
                                                ('Phone', '_phone#await'),
                                                ('CV', '_cv#await'),
                                                ('Native Language', '*native_language'))],
            '*placement':               [None, None, ((('Start Test', '*start_test'),
                                                    ('Continue test', '*continue_test'),
                                                    ('Check result', '/check_result')),
                                                    {'test': ('answers', 'In progress')})],
            '*start_test':              (HELLO_STRING, (('I am ready!', '*q1'))),
            # '*continue_test':           ('You have test in progress', (('I am ready!', _continue_test))),
}
NEW_C, ANSWERS = add_questions()
EDIT_MESSAGE_TEXT = {**EDIT_MESSAGE_TEXT, **NEW_C}
pprint.pprint(EDIT_MESSAGE_TEXT)
pprint.pprint(ANSWERS)


TelePot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)


class TelegramRequest:

    def __init__(self, request):
        self.message_body = json.loads(request)
        self.message_type = self.flavor()
        self.user = self.get_user()
        self.session = None
        self.response = None
        self.inline_message = None
        self.back = None
        self.root = None
        self.internal_commands = {
                                 '_init_session':            (self.initialize_session, None),
                                 '_cancel_session':          (self.update_session, {'is_active': False}),
                                 '_notice_on':               (self.update_user_details, {'notice': True}),
                                 '_notice_off':              (self.update_user_details, {'notice': False}),
                                 '_apply':                   (self.apply, None),
                                # '_session_excellent':       (self.update_session, {'student_confirm': True, 'rate': 5,
                                #                                               'is_going': False, 'is_active': False}),
                                # '_session_nice':            (self.update_session, {'student_confirm': True, 'rate': 4,
                                #                                               'is_going': False, 'is_active': False}),
                                # '_session_terrible':        (self.update_session, {'student_confirm': True, 'rate': 3,
                                #                                               'is_going': False, 'is_active': False}),
                                # '_session_done':            (self.update_session, {'tutor_confirm': True}),
                                # '_t_session_canceled':      (self.update_session, {'tutor_confirm': True, 'rate': 0}),
                                # '_s_session_canceled':      (self.update_session, {'tutor_confirm': True, 'is_going': False,
                                #                                                       'rate': 0, 'is_active': False})
                                }
        pprint.pprint(self.message_body)  # Print to check request
        self.fork()

    def flavor(self):
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
        if isinstance(self.message_body, dict):
            if 'callback_query' in self.message_body:
                return 'callback_query'
            elif 'message' in self.message_body:
                return 'chat'
            elif 'edited_message' in self.message_body:
                return 'edited_message'
            else:
                return 'unrecognized'

    def get_user_credential(self):
        """
        :param msg: dict - received from telegram user(unserialized data JSON -> dict)
        :param msg_type: read return: of flavor(msg)
        :return:
        """
        _chat = None
        if self.message_type == 'chat':
            if 'chat' in self.message_body['message']:
                _chat = self.message_body['message']['chat']
        elif self.message_type == 'callback_query':
            if 'chat' in self.message_body['callback_query']['message']:
                _chat = self.message_body['callback_query']['message']['chat']
        elif self.message_type == 'edited_message':
            if 'chat' in self.message_body['edited_message']:
                _chat = self.message_body['edited_message']['chat']
        ###################### should be rewoked #########################
        elif self.message_type == 'unrecognized':
            return None, None, None
        ##################################################################
        name = _chat['first_name']
        chat_id = _chat['id']
        chat_type = _chat['type']
        return name, chat_id, chat_type

    def fork(self):
        if self.message_type == 'chat':
            message = self.message_body['message']
            self.chat_handler(message)
            return True if self.chat_response() else False
        elif self.message_type == 'callback_query':
            callback = self.message_body['callback_query']
            self.callback_handler(callback)
            self.back_handler(data=callback['data'])
            return True if self.callback_response(callback) else False

    def chat_response(self):
        reply_markup = None
        if self.response[1]:
            reply_markup = self.make_inline_keyboard()
        TelePot.sendMessage(self.user.chat_id, self.response[0](), reply_markup=reply_markup)

    def callback_response(self, callback):
        reply_markup = None
        if self.response:
            if len(self.response) == 3:
                # Only if it needs to replace a button
                self.replaceable_button(buttons=self.response[2][0], condition=self.response[2][1])
                # return just inline key board
            reply_markup = self.make_inline_keyboard()
            print(reply_markup)
        if isinstance(self.response[0], str):
            # send a message to user (above inline buttons)
            try:
                TelePot.editMessageText((telepot.message_identifier(msg=callback['message'])),
                                    text=self.response[0],
                                    reply_markup=reply_markup)
            except telepot.exception.TelegramError:
                self.inline_message = self.response[0]
        elif isinstance(self.response[0], types.FunctionType):
            # send a message below inline buttons
            TelePot.sendMessage(self.user.chat_id,
                                text=self.response[0]())
        elif reply_markup:
            # send a key board to user
            TelePot.editMessageReplyMarkup(telepot.message_identifier(msg=callback['message']),
                                           reply_markup=reply_markup)
        if self.inline_message:
            # send an inline message
            TelePot.answerCallbackQuery(callback['id'],
                                        text=self.inline_message)

    def chat_handler(self, message):
        content_type = telepot.glance(message, self.message_type)[0]
        _cache = cache.get(str(self.user.chat_id))
        if content_type == 'text':
            text = message['text']
            if _cache:
                self.update_user_details(details={_cache: text})
            else:
                command = message['text'].split()
                self.command_handler(cmd=command[0])
        elif content_type == 'document':
            document = message['document']
            destination = settings.MEDIA_ROOT + '/' + document['file_name']
            TelePot.download_file(document['file_id'], dest=destination)
            if _cache:
                self.update_user_cv(file_path=destination, file_name=document['file_name'])
            else:
                self.command_handler(cmd='/_whaaaat?')
        cache.delete(str(self.user.chat_id))

    def callback_handler(self, callback):
        self.root = callback['message']['reply_markup']['inline_keyboard'][0][0]['callback_data']
        data = callback['data']
        if data[0] == '*' or data[0] == '/':
            self.command_handler(data)
        elif data[0] == '_':
            self.internal_command_handler(data)
        elif 'back_to' in data:
            back = data.split('#')
            self.command_handler(cmd=back[-2])
            del back[-1]
            self.root = '#'.join(back)
        elif data == 'on_top':
            self.command_handler(cmd='*root')
            self.root = 'back_to #*root'
        # _answer = check_session_confirm(interlocutor=interlocutor)
        # if _answer is not None:
        #     answer = _answer
        # if data in ['connect', 'skip'] or 'connect' in data:
        #     if 'connect' in data:
        #         student_chat_id = data.split(" ")[1]
        #         notice_student(student_chat=student_chat_id, user=interlocutor)
        #         answer = _command_handler(cmd='*connect')
        #     if data == 'skip':
        #         answer = _command_handler(cmd='*skip')
        # elif data in ['confirm', 'reject'] or 'confirm' in data:
        #     if 'confirm' in data:
        #         tutor_chat_id = data.split(" ")[1]
        #         tutor = TelegramUser.objects.get(chat_id=tutor_chat_id)
        #         tutor.notice = False
        #         tutor.save()
        #         answer = "To start session follow the link {url}".format(url=tutor.appear)
        #         notice_tutor(tutor=tutor)
        #         self.update_session(interlocutor, details={'tutor': tutor, 'is_going': True})
        #     if data == 'reject':
        #         answer = _command_handler(cmd='*reject')

    def result_counting(self, question_id, answer_id):
        # before first question result should be 0
        # else result from dict for current user
        test, is_created = TelegramTest.objects.get_or_create(user=self.user)
        test.current_question = question_id
        _answers = json.dumps({question_id: answer_id})
        if test.answers is None:
            test.answers = json.dumps({"test": {question_id: answer_id}})
            test.result = 'In progress'
        else:
            loaded_answer = json.loads(test.answers)
            loaded_answer['test'].update({question_id: answer_id})
            test.answers = json.dumps(loaded_answer)
        test.save()

    def command_handler(self, cmd):
        """
        :param cmd: str. It's a command(/) or internal command to change message(*) or text message (from user)
        :return: tuple or None . It contains 3 params.
        result[0] - function() which return always str
        result[1] - None or InlineKeyboardMarkup()
        result[2] - None or str 'tutor'/'student' to check access a user to a command
        """
        _blank = EDIT_MESSAGE_TEXT
        if cmd[0] == '/':
            _blank = COMMANDS
        elif cmd[0] == '*':
            data = cmd.split('#')
            if len(data) == 3:
                field, next_question, param = data
                self.result_counting(question_id=field[2:], answer_id=param)
                if next_question == '*q121':
                    cmd = '*root'
                else:
                    cmd = next_question
        self.response = _blank.get(cmd.lower(), COMMANDS['/_whaaaat?'])

    def internal_command_handler(self, cmd):
        data = cmd.split('#')
        if len(data) == 1:
            func, param = self.internal_commands.get(cmd.lower(), None)
            func(param)
        elif len(data) == 2:
            field, param = data
            if param == 'await':
                cache.set('{chat_id}'.format(chat_id=self.user.chat_id), '{field}'.format(field=field[1:]), 90)
                self.command_handler(cmd=self.root.split('#')[-1])
                verb = 'type'
                if field == '_cv':
                    verb = 'upload'
                self.response[0] = 'Please {verb} your {field}'.format(verb=verb, field=field[1:].upper())
            else:
                self.update_user_details(details={field[1:]: param})

    def back_handler(self, data):
        print(self.root)
        if self.root == '*placement':
            self.back = 'back_to #*root#{line}'.format(line=data)
        elif self.root == 'back_to #*root':
            self.back = None
        elif len(self.root) < len(data) or data[0] == '_':
            self.back = self.root
        else:
            data = data.split('#')
            if len(data) == 3:
                data = data[1]
                self.back = self.root + '#{line}'.format(line=data)
                while len(self.back) > 64:  # Telegram API callback_data  1-64 bytes  | 1B = 1 character
                    self.back = self.back.split('#')
                    del self.back[-5]
                    self.back = '#'.join(self.back)
            else:
                data = ''.join(data)
                self.back = self.root + '#{line}'.format(line=data)

    def make_inline_keyboard(self):
        """
        :return: replay_markup(inline keyboard)
        """
        _button_set = []
        if self.response[1] is None:
            return None
        for text, data in self.response[1]:
            _button_set.append([(InlineKeyboardButton(text=text, callback_data=data))])
        if self.back:
            _button_set.insert(0, [(InlineKeyboardButton(text='Back', callback_data=self.back))])
            _button_set.append([(InlineKeyboardButton(text='On Top', callback_data='on_top'))])
        return InlineKeyboardMarkup(inline_keyboard=_button_set)

    def replaceable_button(self, buttons, condition):
        index = 0
        if len(condition) == 1:
            for key, value in condition.items():
                if key == 'session':
                    self.get_session(details={'student': self.user.id, value[0]: value[1]})
                    if self.session:
                        index = 0
                    else:
                        index = 1
                elif key == 'user':
                    if self.user.serializable_value(value[0]) == value[1]:
                        index = 1
                    else:
                        index = 0
                elif key == 'test':
                    try:
                        test = TelegramTest.objects.get(user=self.user)
                        if test.result == value[0]:
                            index = 0
                        else:
                            index = 1
                    except TelegramTest.DoesNotExist:
                        index = 1
        self.response[1] = buttons[:index] + buttons[index + 1:]

    def update_user_cv(self, file_path, file_name):
        fh = open(file_path, "r")
        if fh:
            file_content = ContentFile(fh.read())
            self.user.cv.save(content=file_content, name=file_name)
            fh.close()
            if fh.closed:
                os.remove(fh.name)
            del fh
            cmd = '/_details_updated'
        else:
            cmd = None
        self.command_handler(cmd=cmd)

    def update_user_details(self, details):
        try:
            if TelegramUser.objects.filter(pk=self.user.pk).update(**details):
                self.user.refresh_from_db()
                self.update_handler(details)
        except ValidationError:
            self.inline_message = "Details hasn't been updated"

    def get_user(self):
        first_name, chat_id, chat_type = self.get_user_credential()
        user, is_created = TelegramUser.objects.get_or_create(chat_id=chat_id,
                                                              name=first_name,
                                                              chat_type=chat_type)
        if is_created:
            TelePot.sendMessage(user.chat_id, 'Hi {username}'.format(username=user.name))
        return user

    def get_session(self, details):
        """
        :param details: dict.
        :return:
        """
        try:
            self.session = TelegramSession.objects.get(**details)
        except TelegramSession.DoesNotExist:
            self.session = None

    def update_session(self, details):
        """
        :param details: dict. {field: value}
        :return: True or False
        """
        try:
            self.session = TelegramSession.objects.filter(Q(student=self.user) | Q(tutor=self.user)).update(**details)
            self.update_handler(details)
            self.command_handler(cmd=self.root.split('#')[-1])
            self.response[0] = 'Session: canceled'
            self.inline_message = 'Session status has been canceled'
        except ValidationError:
            self.inline_message = "Unknown Error"

    def initialize_session(self, param=None):
        """
        :return: class TelegramSession and True if created() False if get()
        """
        self.session, is_created = TelegramSession.objects.get_or_create(student=self.user,
                                                                language=self.user.learning_language,
                                                                is_active=True)
        if is_created:
            self.command_handler(cmd=self.root.split('#')[-1])
            self.response[0] = 'Session: active'
            self.inline_message = 'Session has been created'

    def update_handler(self, details):
        for name, val in details.items():
            if isinstance(val, bool):
                val = _notice_handler(val)
            self.inline_message = '{name}: {val}'.format(name=name.title(), val=val.title())
            try:
                self.command_handler(cmd=self.root.split('#')[-1])
                self.response[0] = '{name}: {val}'.format(name=name.title(), val=val.title())
            except AttributeError:
                self.command_handler('/_details_updated')

    def apply(self):
        """send email and a message when tutor is applied"""
        if self.user.cv is not None and self.user.phone is not None and self.user.appear is not None:
            subject = 'New Tutor'
            message = 'Hi Admin, {name} applied as a tutor. Chat ID - {chat_id}'.format(name=self.user.name,
                                                                                        chat_id=self.user.chat_id)
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [settings.EMAIL_FOR_NOTIFICATION]
            send_mail(subject, message, email_from, recipient_list)
            if TelePot.sendMessage(chat_id=settings.TELEGRAM_ADMIN_CHAT_ID, text=message):
                return True
        return False


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
            if TelegramRequest(request_body):
                return JsonResponse({}, status=200)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')




