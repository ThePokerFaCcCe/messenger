from typing import Any, Optional
from cryptography.fernet import InvalidToken
from django.conf import settings
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.db.models.base import Model
from django.db.models.fields import CharField, DateTimeField
from django.db.models.manager import Manager
from django.db.models.enums import TextChoices
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import BasePasswordHasher, PBKDF2PasswordHasher, make_password, check_password
from encrypt_decrypt_fields import Crypto


def hash_token(token, hasher=None):
    """Return hashed token"""
    return make_password(token, hasher=hasher)


def encrypt_token_and_value(encrypt_key, value, token) -> bytes:
    """Return encrypted string with this format: '`value`@`token`'"""
    return Crypto(encrypt_key).encrypt(f"{value}@{token}")


def decrypt_token_and_value(encrypt_key, encrypted_text: str
                            ) -> Optional[tuple[str, str]]:
    """Return a tuple that contains (value, token) if 
    `encrypted_text` is valid else return `None`"""

    try:
        decrypted_value = Crypto(encrypt_key).decrypt_token(
            bytes(encrypted_text, encoding='utf-8')
        )
    except InvalidToken:
        return None

    splitted_value = decrypted_value.split("@", 1)
    if len(splitted_value) == 2 and all(splitted_value):
        return splitted_value


def generate_token(instance=None, length=24, key=None, hasher: BasePasswordHasher = None):
    """Return auto-generated hashed token and set `_unhashed_token` 
    to unhashed token in instance if `instance` is passed.

    Parameters
    ----------
    `length` will read from `_token_length` attr if exists in `instance`(default is 24).

    `hasher` will read from `_hasher` attr if exists in `instance`(default is None)."""

    if instance:
        length = getattr(instance, '_token_length', length)
        hasher = getattr(instance, '_hasher', hasher)

    token = get_random_string(length=length)
    hashed_token = hash_token(token, hasher)

    if instance:
        setattr(instance, "_unhashed_token", token)
    return hashed_token


class EncryptedTokenManager(Manager):
    def find_token(self, encrypted_token) -> Optional[Any]:
        key = getattr(self.model, '_encrypt_key', None)
        assert key is not None, "You must set `_encrypt_key` attr in your model"

        if value := decrypt_token_and_value(key, encrypted_token):
            instance_id, token = value

            if instance := self.filter(pk=instance_id):
                instance = instance[0]

                if self.check_token(token, instance.token):
                    return instance

    @classmethod
    def check_token(cls, token: str, hashed_token: str) -> bool:
        """Return `True` if raw `token` is same as `hashed_token`"""
        return check_password(token, hashed_token)


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
