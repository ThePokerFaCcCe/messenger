
from typing import Optional
from django.db.models.base import Model
from django.db.models.manager import Manager
from django.contrib.auth.hashers import check_password

from user.models.utils.token import decrypt_token_and_value


class EncryptedTokenManager(Manager):
    def find_token(self, encrypted_token) -> Optional[Model]:
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
