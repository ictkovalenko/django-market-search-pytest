from django.apps import AppConfig


class SystemConfig(AppConfig):
    name = 'web.system'
    verbose_name = 'System'

    def ready(self):
        pass
