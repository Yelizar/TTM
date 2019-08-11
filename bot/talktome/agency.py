import json
import logging

from .register import UserRegister
from .user import UserController


logger = logging.getLogger('telegram.bot')


class talktome:

    @staticmethod
    def process(request):
        """
        @raises ValueError
        """
        raw = request.body.decode('utf-8')
        logger.info(raw)

        payload = json.loads(raw)

        # doto: can we use use user_id instead chat_id?
        chat_id = payload['message']['chat']['id']
        cmd = payload['message'].get('text')


        UserRegister.register[chat_id] = UserRegister.register.get(chat_id, UserController.newUser(payload['message']['from']))

        return UserController.processCommand(chat_id, cmd)


