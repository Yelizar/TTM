from django.apps import AppConfig


class SessionConfig(AppConfig):
    name = 'website.session'

    def ready(self):
        # noinspection PyUnresolvedReferences
        import website.session.signals

