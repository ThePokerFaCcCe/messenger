from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .message import Message

User = settings.AUTH_USER_MODEL


class Seen(models.Model):
    message = models.ForeignKey(to=Message, on_delete=models.CASCADE,
                                related_name="seen_users")
    user = models.ForeignKey(to=User, null=True, on_delete=models.SET_NULL,
                             related_name="seen_messges")

    seen_at = models.DateField(_("Seen at"), auto_now_add=True)

    class Meta:
        ordering = ['-seen_at']
        unique_together = ['user', 'message']
