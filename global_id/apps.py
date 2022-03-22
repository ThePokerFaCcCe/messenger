from django.apps import AppConfig


class GlobalIdConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'global_id'

    def ready(self) -> None:
        from . import signals
