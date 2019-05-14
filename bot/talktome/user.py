import json
from ..utils import parse_planetpy_rss
from django.template.loader import render_to_string

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
            'wallet' : {
                'debugAccaunt' : 0,
                'trialAccount' : 1,
                'tokenAccount' : 0,
            },
        }

        Users[chat_id] = new_user

    role = Users[chat_id]['role']


    file_name = handlers.get(role)
    return render_to_string(file_name)

def _display_planetpy_feed(chat_id):
    return render_to_string('talktome/link_list.md', {'items': parse_planetpy_rss()})

def _learner_register(chat_id):
    Users[chat_id]['role'] = UserRole.USER_LEARNER
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


def _tutor_pending_list():
    """Output first 10 tutors from pending list
    """
    items = []

    for u_key, u_value in Users.items():
        if u_value['role'] == UserRole.USER_TUTOR:
            item = {}
            item['title'] = u_key
            item['link'] = u_value['role']

            items.append(item)

    return items[:10]

def _admin_display_denping_list(chat_id):
    return render_to_string('talktome/link_list.md', {'items': _tutor_pending_list()})
