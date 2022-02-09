from typing import Optional
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .community_chat import CommunityChat
from .invite_link import InviteLink

User = settings.AUTH_USER_MODEL


class Member(models.Model):
    class RankChoices(models.IntegerChoices):
        OWNER = 3, _("Owner")
        ADMIN = 2, _("Admin")
        NORMAL = 1, _('Normal')
        RESTRICTED = 0, _('Restricted')
        BANNED = -1, _('Banned')

    rank = models.IntegerField(_("Rank"),
                               choices=RankChoices.choices,
                               default=RankChoices.NORMAL)

    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             related_name='chat_members')
    community = models.ForeignKey(to=CommunityChat,
                                  on_delete=models.CASCADE,
                                  related_name='members')
    _used_link = models.ForeignKey(
        to=InviteLink, null=True, on_delete=models.SET_NULL,
        related_name='members_used',
        help_text=_(
            "The link that member used to join if "
            "joined by link"
        )
    )
    used_guid = models.CharField(
        _("Used guid"), null=True, blank=True,
        max_length=60, help_text=_(
            "The guid that member used to join if "
            "joined by guid"
        ))

    @property
    def used_link(self) -> Optional[str]:
        if (link := self._used_link):
            return link.link

    @property
    def joined_by(self) -> Optional[str]:
        if self.used_guid:
            return 'used_guid'
        if self._used_link:
            return 'used_link'
        return None
