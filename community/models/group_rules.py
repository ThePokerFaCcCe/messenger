from django.db import models
from django.utils.translation import gettext_lazy as _


class GroupRules(models.Model):
    can_send_message = models.BooleanField(
        _("Can send message"), default=True,
        help_text=_("Members can send message or not")
    )

    can_add_member = models.BooleanField(
        _("Can add member"), default=True,
        help_text=_("Members can add member or not")
    )
