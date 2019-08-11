import json
from datetime import datetime

USERS_DUMP_FILE = "talktome.users.json"
USERS_BACKUP_FILE = "talktome.{%y.%m.%d.%H.%M.%S}.users.bk"

class UserRegister(object):

    register = {}

    def __init__(self, ):
        UserRegister.load()

    @staticmethod
    def save():
        return UserRegister.__save(USERS_DUMP_FILE)

    @staticmethod
    def load():
        UserRegister.__save(USERS_BACKUP_FILE.format(datetime.now()))
        return UserRegister.__load(USERS_DUMP_FILE)

    @staticmethod
    def __save(filename, encoding='utf-8'):
        with open(filename, mode='w', encoding=encoding) as f:
            json.dump(UserRegister.register, f, indent=2)
        return len(UserRegister.register)

    @staticmethod
    def __load(filename, encoding='utf-8'):
        with open(filename, mode='r', encoding=encoding) as f:
            UserRegister.register = json.load(f)
        return len(UserRegister.register)
