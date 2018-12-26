from django.apps import AppConfig


class BusinessConfig(AppConfig):
    name = 'web.businesses'
    verbose_name = "Businesses"

    def ready(self):
        from . import signals
