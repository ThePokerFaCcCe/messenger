from django.dispatch import Signal

user_online = Signal(providing_args=['instance'])
