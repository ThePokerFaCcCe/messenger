from django.db.models.manager import BaseManager

from user.models.queryset import VerifyCodeQuerySet


class VerifyCodeManager(BaseManager.from_queryset(VerifyCodeQuerySet)):

    def delete_expired(self) -> None:
        """Delete expired codes"""
        self.get_queryset().filter_expired().delete()
