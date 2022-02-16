from django.db import models
from django.utils.translation import gettext_lazy as _

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
            self.save()

    class Meta:
        abstract = True
