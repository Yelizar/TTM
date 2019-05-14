import json
import logging

from .user import _display_help, _learner_register, _tutor_register, _admin_dump, _admin_load, _admin_display_denping_list, _display_planetpy_feed

commands = {
    '/start': _display_help,
    '/help': _display_help,
    '/learner': _learner_register,
    '/tutor': _tutor_register,
    '/dump': _admin_dump,
    '/load': _admin_load,
    '/pending': _admin_display_denping_list,

    'feed': _display_planetpy_feed,
}

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

        chat_id = payload['message']['chat']['id']
        user_id = payload['message']['user']['id']
        cmd = payload['message'].get('text')  # command

        func = commands.get(cmd.split()[0].lower())
        if func:
            return chat_id, func(chat_id)
        else:
            return chat_id, 'I do not understand you, mate!'

