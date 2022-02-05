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
    used_link = models.ForeignKey(
        to=InviteLink, null=True, on_delete=models.SET_NULL,
        related_name='members_used',
        help_text=_(
            "The link that member used to join if "
            "joined by link"
        )
    )
    is_joined_by_guid = models.BooleanField(
        _("Is used guid"), default=False,
        help_text=_("Is member joined by guid"))

    @property
    def joined_by(self) -> str:
        if self.is_joined_by_guid:
            return 'guid'
        return 'link'
