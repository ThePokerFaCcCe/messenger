from typing import Optional
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, models

from global_id.models import GUID


class GUIDMixin(models.Model):
    __new_guid = None
    __update_guid = None

    _guid = GenericRelation(
        to=GUID,
        object_id_field="chat_id",
        content_type_field="chat_content_type",
    )

    @property
    def guid(self) -> Optional[str]:
        """Return guid text if exists else None"""
        if (g_id := self._guid.first()):
            return g_id.guid

    @guid.setter
    def guid(self, new_id: str):
        """Set new id for guid, it automatically
        creates GUID model if doesn't exists."""

        g_id = self._guid.first()
        if g_id is None:
            self.__new_guid = GUID(
                guid=new_id
            )
            self.__new_guid.clean_guid()

        else:
            g_id.guid = new_id
            g_id.clean_guid()
            self.__update_guid = g_id

    @guid.deleter
    def guid(self):
        self._guid.all().delete()

    def save(self, *args, **kwargs):
        with transaction.atomic():
            r = super().save(*args, **kwargs)
            if (g_id := self.__new_guid):
                self._guid.add(g_id, bulk=False)
            elif (g_id := self.__update_guid):
                g_id.save()
            return r

    class Meta:
        abstract = True
