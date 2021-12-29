from typing import Optional
from django.conf import settings
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.db.models.base import Model
from django.db.models.fields import CharField, DateTimeField
from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import BasePasswordHasher, PBKDF2PasswordHasher

from user.models.manager import EncryptedTokenManager
from user.models.utils.token import (encrypt_token_and_value,
                                     generate_token)


class Device(Model):
    _token_length = 32
    _hasher: BasePasswordHasher = PBKDF2PasswordHasher()
    _encrypt_key = settings.DEVICETOKEN_KEY
    _unhashed_token = None

    objects = EncryptedTokenManager()

    class TypeChoices(TextChoices):
        WINDOWS = 'windows', 'Windows'
        ANDROID = 'android', 'Android'
        IOS = 'ios', 'IOS'
        OTHER = 'other', 'Other'

    type = CharField(_("Device type"), max_length=15, choices=TypeChoices.choices)
    model = CharField(_("Device model"), max_length=50)

    token = CharField(db_index=True, max_length=128, editable=False,
                      verbose_name=_("Device token"), auto_created=True)
    created_at = DateTimeField(auto_now_add=True)

    user = ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=CASCADE)

    @property
    def unhashed_token(self) -> Optional[str]:
        """Only return generated unhashed token 
        when model is just created. otherwise return `None`"""
        return self._unhashed_token

    def save(self, *args, **kwargs):
        editing = bool(self.token)
        if not editing:
            self.token = generate_token(instance=self)
        super().save(*args, **kwargs)
        if not editing:
            self.__encrypt_unhashed_token()

    def __encrypt_unhashed_token(self):
        """Encrypts `_unhashed_token` and `pk` together and set it
         to `_unhashed_token`. You need to set `_encrypt_key` attr """

        self._unhashed_token = encrypt_token_and_value(
            self._encrypt_key,
            self.pk,
            self._unhashed_token
        ).decode("utf-8")
