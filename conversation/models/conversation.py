from typing import Type
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from conversation.models import PrivateChat

User = settings.AUTH_USER_MODEL


def get_model_type(model: Type[models.Model],
                   instance=None) -> str:
    if issubclass(model, PrivateChat):
        return Conversation.TypeChoices.PRIVATE

    return getattr(instance, "type", None)


class Conversation(models.Model):
    class TypeChoices(models.TextChoices):
        GROUP = 'GP', _('Group')
        PRIVATE = 'PV', _('Private')

    type = models.CharField(choices=TypeChoices.choices,
                            auto_created=True, max_length=2)

    alias = models.CharField(_("Alias"), null=True, blank=True, max_length=64)
    is_pinned = models.BooleanField(_("Pinned"), default=False)
    is_archived = models.BooleanField(_("Archived"), default=False)

    # is_deleted = models.BooleanField(_("Is deleted"),
    #                                  default=False, db_index=True,
    #                                  help_text=_("Is chat deleted or not"))
    created_at = models.DateTimeField(auto_now_add=True)

    chat_content_type: ContentType = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE)
    chat_id = models.BigIntegerField()
    chat = GenericForeignKey(
        ct_field="chat_content_type",
        fk_field="chat_id"
    )

    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             related_name='chats')

    def save(self, *args, **kwargs):
        if not self.type:
            model = self.chat_content_type.model_class()
            self.type = get_model_type(model, self.chat)
        super().save(*args, **kwargs)
