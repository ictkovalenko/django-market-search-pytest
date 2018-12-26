from django.apps import AppConfig


class SearchConfig(AppConfig):
    name = 'web.search'
    verbose_name = "Search"

    def ready(self):
        from . import signals
