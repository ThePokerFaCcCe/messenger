from django.db import models
from django.core import validators
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .utils import (generate_invite_link, INVITE_LINK_REGEX,
                    INVITE_LINK_MAX_LENGTH)
from . import CommunityChat


class InviteLink(models.Model):
    link = models.CharField(
        _("Invite link"), default=generate_invite_link,
        db_index=True, unique=True,
        max_length=INVITE_LINK_MAX_LENGTH,
        validators=[
            validators.RegexValidator(INVITE_LINK_REGEX),
        ])

    chat = models.ForeignKey(to=CommunityChat, null=True,
                             on_delete=models.SET_NULL,
                             related_name='invite_links')

    is_deleted = models.BooleanField(
        _("Is deleted"), default=False,
        help_text=_("Is link deleted or not")
    )

    created_at = models.DateTimeField(_('Created at'),
                                      auto_now_add=True)
    deleted_at = models.DateTimeField(
        _("Deleted at"), null=True, blank=True,
        auto_created=True)

    def save(self, *args, **kwargs):
        if self.is_deleted and self.deleted_at is None:
            self.deleted_at = timezone.now()
        return super().save(*args, **kwargs)
