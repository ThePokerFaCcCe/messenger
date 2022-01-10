from typing import Optional
from cryptography.fernet import InvalidToken
from django.conf import settings
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.db.models.base import Model
from django.db.models.fields import BooleanField, DateTimeField, PositiveSmallIntegerField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from encrypt_decrypt_fields import EncryptedBinaryField, Crypto
from datetime import timedelta
from random import randint

from core.models.base import BaseToken
from .manager import VerifyCodeManager


class VerifyCode(BaseToken, Model):
    _token_length = 42
    _encrypt_key = settings.VERIFYCODETOKEN_KEY

    max_digit = 6
    """Max digits for generating code"""

    validation_regex = r'^(\d)*$'
    """Regex for validating sent code by user"""

    find_code_regex = r'\d{6}'
    """Regex for finding code in email text (used for tests)"""

    def generate_code(*args, **kwargs) -> str:
        """Returns 6-digit unique code"""
        numbers = []

        i = 0
        while i < VerifyCode.max_digit:
            num = randint(0, 9)
            if i != 0:
                prev_num = int(numbers[i-1])
                if any([
                    num == prev_num,
                    num+1 == prev_num,
                    num-1 == prev_num,
                ]):
                    continue
            numbers.append(str(num))
            i += 1

        return ''.join(numbers)

    expire_after = timedelta(minutes=1)
    max_tries = 3

    _expires_at = None
    _dec_code = 0

    objects = VerifyCodeManager()

    _code = EncryptedBinaryField(verbose_name=_("Code"), auto_created=True,
                                 key=settings.VERIFYCODE_KEY, editable=False,
                                 default=generate_code, db_index=True)

    _tries = PositiveSmallIntegerField(default=0)
    is_used = BooleanField(default=False, db_index=True)

    created_at = DateTimeField(_("Created at"), auto_now_add=True, editable=False)

    user = ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=CASCADE,
                      related_name='verify_codes')

    @property
    def code(self) -> Optional[str]:
        """Return decrypted code if key was correct, else None"""
        if self._dec_code == 0:
            try:
                self._dec_code = Crypto(settings.VERIFYCODE_KEY).decrypt_token(
                    self._code if isinstance(self._code, bytes)
                    else bytes(self._code, 'utf-8')
                )
            except InvalidToken:
                self._dec_code = self._code if len(self._code) == self.max_digit else None
        return self._dec_code

    @property
    def expires_at(self) -> timezone:
        if self._expires_at is None:
            self._expires_at = self.created_at + self.expire_after
        return self._expires_at

    @property
    def email(self) -> str:
        return self.user.email

    @expires_at.setter
    def expires_at(self, value: timezone):
        self._expires_at = value

    @property
    def is_expired(self) -> bool:
        """Returns `True` if `expire_date` passed or `max_tries` exceeded"""
        return (
            self.is_used
            or (timezone.now() - self.created_at) > self.expire_after
            or self._tries >= self.max_tries
        )

    @property
    def tries(self) -> int:
        return self._tries

    def increase_tries(self, save: bool = False, **save_kwargs) -> int:
        """Increase `tries` by 1 and return new `tries`

        Parameters
        ----------
        `save : bool` Save new tries to database

        `**save_kwargs` Kwargs that need to pass when calling `.save()`
        """
        self._tries += 1
        if save:
            self.save(**save_kwargs)

        return self.tries

    def check_code(self, code) -> bool:
        """Checks if entered code is same as encrypted code"""
        return code == self.code

    def should_generate_token(self) -> bool:
        return self.is_used

    def email_code(self):
        self.user.email_user('Login code', f"Your login code is {self.code}")
