from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import PBKDF2PasswordHasher

from core.models.base import BaseToken
from user.models import Device


class Access(BaseToken):
    _token_length = 64
    _hasher = PBKDF2PasswordHasher()
    _encrypt_key = settings.ACCESSTOKEN_KEY

    ip = models.GenericIPAddressField(null=True, blank=True)
    last_used = models.DateTimeField(_("Last used"), null=True, blank=True,
                                     help_text=_("Last time this token used"))
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="accesses")
    device = models.ForeignKey(to=Device, on_delete=models.CASCADE,
                               related_name="accesses")
