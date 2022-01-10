from django.db.models.manager import BaseManager

from core.models.manager import EncryptedTokenManager
from ..queryset import VerifyCodeQuerySet


class VerifyCodeManager(BaseManager.from_queryset(VerifyCodeQuerySet),
                        EncryptedTokenManager):

    def delete_expired(self) -> None:
        """Delete expired codes"""
        self.get_queryset().filter_expired().delete()
