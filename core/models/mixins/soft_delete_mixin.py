from django.db import models
from django.utils.translation import gettext_lazy as _

from core.signals import pre_soft_delete, post_soft_delete
from ..manager import SoftDeleteManager


class SoftDeleteMixin(models.Model):
    objects = SoftDeleteManager()

    is_deleted = models.BooleanField(
        _("Is deleted"), default=False,
        help_text=_("Is item deleted or not")
    )

    def soft_delete(self):
        """Set `is_deleted` field to `True`"""
        if not self.is_deleted:
            self.is_deleted = True
            pre_soft_delete.send(sender=self.__class__, instance=self)
            self.save()
            post_soft_delete.send(sender=self.__class__, instance=self)

    class Meta:
        abstract = True
