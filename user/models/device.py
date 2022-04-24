from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import PBKDF2PasswordHasher

from core.models.base import BaseToken


class Device(BaseToken):
    _token_length = 32
    _hasher = PBKDF2PasswordHasher()
    _encrypt_key = settings.DEVICETOKEN_KEY

    class TypeChoices(models.TextChoices):
        WINDOWS = 'windows', 'Windows'
        ANDROID = 'android', 'Android'
        IOS = 'ios', 'IOS'
        OTHER = 'other', 'Other'

    type = models.CharField(_("Device type"), max_length=15, choices=TypeChoices.choices)
    model = models.CharField(_("Device model"), max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="devices")
