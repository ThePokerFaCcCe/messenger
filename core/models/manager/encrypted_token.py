
from typing import Iterable, Optional
from django.db.models.base import Model
from django.db.models.manager import Manager
from django.contrib.auth.hashers import check_password

from ..utils.token import decrypt_token_and_value


class EncryptedTokenManager(Manager):
    def find_token(self, encrypted_token, select: Iterable[str] = None,
                   prefetch: Iterable[str] = None) -> Optional[Model]:
        """Find object by encrypted token that contains
        pk and unencrypted token

        Parameters
        ----------
        `select`: a list of strings that used for `.select_related()`

        `prefetch`: a list of strings that used for `.prefetch_related()`
        """
        prefetch = prefetch if prefetch is not None else []
        select = select if select is not None else []

        if encrypted_token is None:
            return None

        encrypted_token = str(encrypted_token)
        key = getattr(self.model, '_encrypt_key', None)
        assert key is not None, "You must set `_encrypt_key` attr in your model"

        if value := decrypt_token_and_value(key, encrypted_token):
            instance_id, token = value
            instance = self.filter(pk=instance_id)\
                .select_related(*select)\
                .prefetch_related(*prefetch).first()
            if instance:
                if self.check_token(token, instance.token):
                    return instance

    @classmethod
    def check_token(cls, token: str, hashed_token: str) -> bool:
        """Return `True` if raw `token` is same as `hashed_token`"""
        return check_password(token, hashed_token)
