from typing import Optional
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import BasePasswordHasher, PBKDF2PasswordHasher
from django.db import models

from user.models.manager.encrypted_token import EncryptedTokenManager
from user.models.utils.token import encrypt_token_and_value, generate_token


class BaseToken(models.Model):
    """Base token model that have `token` field that hashes auto-generated 
    token. also have `encrypted_token` property that returns encrypted sring 
    contains instance pk and original token that users will get this string 
    as their token, and you can use `find_token` method in default manager 
    to find your instance"""

    _token_length = 32
    """number of chars for creating token"""

    _original_token = None
    """original token (unhashed token)"""

    _hasher: BasePasswordHasher = PBKDF2PasswordHasher()
    """hasher for hashing token"""

    _encrypt_key = settings.SECRET_KEY
    """encryption key for encrypting token that used for `_encrypted_token`"""

    _encrypted_token = None
    """Encrypted token that user will see"""

    objects = EncryptedTokenManager()

    token = models.CharField(db_index=True, max_length=128, editable=False,
                             verbose_name=_("Token"), auto_created=True)

    @property
    def encrypted_token(self) -> Optional[str]:
        """Only return generated encrypted token 
        when model is just created. otherwise return `None`"""
        return self._encrypted_token

    def save(self, *args, **kwargs):
        editing = bool(self.token)
        if not editing:
            self.token = generate_token(instance=self)
        super().save(*args, **kwargs)
        if not editing:
            self.__encrypt_original_token()

    def __encrypt_original_token(self):
        """Encrypts `_original_token` and `pk` together and set it
         to `_encrypted_token`. You need to set `_encrypt_key` attr """

        self._encrypted_token = encrypt_token_and_value(
            self._encrypt_key,
            self.pk,
            self._original_token
        ).decode("utf-8")

    class Meta:
        abstract = True
