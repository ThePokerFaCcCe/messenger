from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from core.models.mixins import SoftDeleteMixin
from core.utils import get_chat_content_type


class Message(SoftDeleteMixin, models.Model):

    chat_content_type = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE,
        related_name='+')
    chat_id = models.BigIntegerField()
    chat = GenericForeignKey(
        ct_field="chat_content_type",
        fk_field="chat_id"
    )

    sender = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='sent_messages', verbose_name=_("Sender"))

    class ContentTypeChoices(models.TextChoices):
        TEXT = 'text', _("Text")
        IMAGE = 'image', _("Image")
        VIDEO = 'video', _("Video")
        FILE = 'file', _("File")
    content_type = models.CharField(_("Content type"), max_length=10, db_index=True,
                                    choices=ContentTypeChoices.choices)
    content_content_type = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE,
        related_name='+')
    content_id = models.BigIntegerField()
    content = GenericForeignKey(
        ct_field="content_content_type",
        fk_field="content_id"
    )

    forwarded_from = models.ForeignKey(to='self', on_delete=models.SET_NULL, null=True,
                                       related_name="forwarded_messages")

    is_edited = models.BooleanField(_("Is edited"), default=False)
    sent_at = models.DateTimeField(_("Sent at"), auto_now_add=True)
    edited_at = models.DateTimeField(_("Edited at"), null=True, blank=True,
                                     auto_created=True)

    def save(self, *args, **kwargs):
        if not (self.pk and self.chat_content_type):
            self.chat_content_type = get_chat_content_type(self.chat_id)

        if self.is_edited and not self.edited_at:
            self.edited_at = timezone.now()
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['-id']

    # Custom message id for every chat idea :
    # message_id = models.PositiveBigIntegerField(
    #     _("Message id"), editable=False,
    #     auto_created=True, db_index=True)

    # def __set_message_id(self):
    #     last_msg = self.__class__.objects\
    #         .only("message_id").filter(
    #             chat_id=self.chat_id
    #         ).first()
    #     self.message_id = (last_msg.message_id+1
    #                        if last_msg else 1)

    # def save(self, *args, **kwargs):
    #     if not self.message_id:
    #         self.__set_message_id()
    #     return super().save(*args, **kwargs)

    # class Meta:
    #     unique_together = ["message_id", "chat_id"]
    #     ordering = ['-message_id']
