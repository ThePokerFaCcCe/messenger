from typing import Type
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from core.models.mixins import SoftDeleteMixin

from picturic.fields import PictureField
from global_id.models.mixins import GUIDMixin
from .group_community import GroupCommunity
from .mixins import NegativeUUIDMixin

User = settings.AUTH_USER_MODEL


def get_model_type(model: Type[models.Model]) -> str:
    if issubclass(model, GroupCommunity):
        return CommunityChat.TypeChoices.GROUP


class CommunityChat(NegativeUUIDMixin, SoftDeleteMixin, GUIDMixin, models.Model):

    class TypeChoices(models.TextChoices):
        GROUP = 'GP', _('Group')
        CHANNEL = 'CH', _('Channel')

    type = models.CharField(choices=TypeChoices.choices,
                            auto_created=True, max_length=2)

    name = models.CharField(_("Name"), max_length=64)
    description = models.TextField(_("Description"), max_length=255,
                                   null=True, blank=True)
    profile_image = PictureField(use_upload_to_func=True,
                                 make_thumbnail=True, null=True)

    creator = models.ForeignKey(
        to=User, on_delete=models.SET_NULL, null=True,
        related_name='created_communities')

    created_at = models.DateTimeField(auto_now_add=True)

    community_content_type: ContentType = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE)
    community_id = models.PositiveIntegerField()
    community = GenericForeignKey(
        ct_field="community_content_type",
        fk_field="community_id"
    )

    def save(self, *args, **kwargs):
        if not self.type:
            model = self.community_content_type.model_class()
            self.type = get_model_type(model)
        super().save(*args, **kwargs)
