from typing import Optional
from cryptography.fernet import InvalidToken
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import BasePasswordHasher, make_password
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
    """Return auto-generated hashed token and set `_original_token` 
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
        setattr(instance, "_original_token", token)
    return hashed_token
