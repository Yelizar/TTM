from django.apps import AppConfig


class TplatformConfig(AppConfig):
    name = 'tplatform'

    def ready(self):
        # noinspection PyUnresolvedReferences
        import tplatform.signals
