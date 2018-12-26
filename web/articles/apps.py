from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    name = 'web.articles'
    verbose_name = "Articles"

    def ready(self):
        from . import signals
