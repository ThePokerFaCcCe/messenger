from django.apps import AppConfig


class MessengerChannelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messenger_channels'

    def ready(self) -> None:
        from . import signals
