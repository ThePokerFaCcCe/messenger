from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core import exceptions
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .validators import GUIDValidator


class GUID(models.Model):
    guid = models.CharField(
        _('Global-Unique-ID'),
        unique=True, null=True, max_length=60, db_index=True,
        help_text=_(('GUID must start with English letters '
                     'and contain numbers and one underscore ( _ ). '
                     '4-60chars only ')),
        validators=[
            GUIDValidator(),
            MinLengthValidator(4, _("GUID must have at least 4 chars")),
            MaxLengthValidator(60, _("GUID can have at last 60 chars")),
        ],
        error_messages={
            'unique': _("This GUID already exists."),
        },)

    chat_content_type: ContentType = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE)
    chat_id = models.PositiveIntegerField()
    chat = GenericForeignKey(
        ct_field="chat_content_type",
        fk_field="chat_id"
    )

    def clean_guid(self):
        if self.__class__.objects.filter(guid=self.guid).exists():
            raise exceptions.ValidationError(
                {"guid": "This GUID already exists."})
