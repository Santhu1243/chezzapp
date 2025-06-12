from django.apps import AppConfig

class NonsapConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nonsap'

    def ready(self):
        import nonsap.signals
from django.apps import AppConfig


class NonsapConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nonsap'

    def ready(self):
        from . import signals



    

