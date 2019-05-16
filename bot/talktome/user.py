import json
from ..utils import parse_planetpy_rss
from django.template.loader import render_to_string

from .register import UserRegister

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

class Controller(object):

    def __init__(self, file_name='talktome/hello.md'):
        self.hello_message_file = file_name
        self.command_list = {
            '/info': display_help,
            'feed' : distlay_planetry_feed,
        }

    def processCommand(self, chat_id, cmd):
        chat_id_ret = chat_id
        string_ret = "I do not understand you, mate!"

        handler = self.command_list.get(cmd.split()[0].lower())
        if handler:
            chat_id_ret, string_ret = handler(self, chat_id, cmd)

        return chat_id_ret, string_ret

    def display_help(self, chat_id, cmd):
        return chat_id, render_to_string(self.hello_message_file)

    def display_planetpy_feed(self, chat_id, cmd):
        return chat_id, render_to_string('talktome/link_list.md', {'items': parse_planetpy_rss()})


class AdminController(Controller):
    admin_command_list = {
        '/restore': restore_register,
        '/dump': dump_register,
    }

    def __init__(self):
        super(AdminController, self).__init__('talktome/admin.md')
        self.command_list.update(AdminController.admin_command_list)

    def restore_register(self, chat_id, cmd):
        return chat_id, "Saved {} users' items".format(UserRegister.save())

    def dump_register(self, chat_id, cmd):
        return chat_id, "Loaded {} users' items".format(UserRegister.load())

#def _tutor_pending_list():
#    """Output first 10 tutors from pending list
#    """
#    items = []
#
#    for u_key, u_value in Users.items():
#        if u_value['role'] == UserRole.USER_TUTOR:
#            item = {}
#            item['title'] = u_key
#            item['link'] = u_value['role']
#
#            items.append(item)
#
#    return items[:10]

#def _admin_display_denping_list(chat_id):
#    return render_to_string('talktome/link_list.md', {'items': _tutor_pending_list()})


class NewbController(Controller):

    def __init__(self):
        super(NewbController, self).__init__('talktome/admin.md')

        newb_commands = {
            '/learner': join_as_learner,
            '/tutor': join_as_tutor,
        }
        self.command_list.update(newb_commands)

    def join_as_learner(self, chat_id, cmd):
        return __join_as_role(chat_id, UserRole.USER_LEARNER, 'talktome/learner.md')

    def join_as_tutor(self, chat_id, cmd):
        return __join_as_role(chat_id, UserRole.USER_TUTOR, 'talktome/tutor.md')

    def __join_as_role(chat_id, role, hello_message_file):
        UserController.update_role(chat_id, role)  
        return chat_id, render_to_string(hello_message_file)


class LearnerController(Controller):

    def __init__(self):
        super(LearnerController, self).__init__('talktome/learner.md')

        learner_commands = {
            '/submit': submit_session,
            '/skip': skip_tutor,
            '/confirm': confirm_tutor,
            '/approve': approve_session,
            '/reject': reject_session,
        }
        self.command_list.update(learner_commands)

    def submit_session(self, chat_id, cmd):
        return chat_id, "submit_session"

    def skip_tutor(self, chat_id, cmd):
        return chat_id, "skip_tutor"

    def confirm_tutor(self, chat_id, cmd):
        return chat_id, "confirm_tutor"

    def approve_session(self, chat_id, cmd):
        return chat_id, "approve_session"

    def reject_session(self, chat_id, cmd):
        return chat_id, "reject_session"


class TutorController(Controller):

    def __init__(self):
        tutor_commands = {
            '/join': join_team,
            '/online': online_status,
            '/offline': offline_status,
            '/confirm': comfirm_ready,
            '/approve': approve_session,
            '/reject': reject_session,
        }

        super(TutorController, self).__init__('talktome/tutor.md')
        self.command_list.update(tutor_commands)

    def join_team(self, chat_id, cmd):
        return chat_id, "join_team"

    def online_status(self, chat_id, cmd):
        return chat_id, "online_status"

    def offline_status(self, chat_id, cmd):
        return chat_id, "offline_status"

    def comfirm_ready(self, chat_id, cmd):
        return chat_id, "comfirm_ready"

    def approve_session(self, chat_id, cmd):
        return chat_id, "approve_session"

    def reject_session(self, chat_id, cmd):
        return chat_id, "reject_session"


ADMIN_CTRL = AdminControler()
NEWB_CTRL = NewbControler()
LEARNER_CTRL = LearnerControler()
TUTOR_CTRL = TutorControler()

CONTROLLERS = {
    UserRole.USER_ADMIN : ADMIN_CTRL,
    UserRole.USER_NEWB : NEWB_CTRL,
    UserRole.USER_LEARNER : LEARNER_CTRL,
    UserRole.USER_TUTOR : TUTOR_CTRL,
}

    handlers = {
        UserRole.USER_ADMIN: 'talktome/admin.md',
        UserRole.USER_NEWB: 'talktome/hello.md',
        UserRole.USER_LEARNER: 'talktome/learner.md',
        UserRole.USER_TUTOR: 'talktome/tutor.md',
    }

class UserController(object):

    @staticmethod
    def processCommand(chat_id, cmd):
        """ Process user request

        @param chat_id user id
        @param cmd string with user request
        """
        user = UserRegister.register.get(chat_id)   # get user form registre
        ctrl = CONTROLLERS[user['role']]            # get controller based on user role
        return ctrl.processCommand(user, cmd)       # call controller's handler to process request

    @staticmethod
    def newUser(descriptor):
        new_user = {
            'from' : descriptor,
            'nativeLang' : LanguageSet.LANG_UNKNOWN,
            'communicationLang' : LanguageSet.LANG_ENG,
            'role' : UserRole.USER_NEWB,
            'bannedByAdmin' : False,
            'wallet' : {
                'debugAccaunt' : 0,
                'trialAccount' : 1,
                'tokenAccount' : 0,
            },
        }

        return new_user

    @staticmethod
    def update_role(chat_id, user_role):
        user = UserRegister.register.get(chat_id)   # get user form registre
        user['role'] = user_role
        UserRegister.register.update({chat_id, user})
