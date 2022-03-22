from typing import Optional
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, models

from core.cache import cache
from global_id.models import GUID


class GUIDMixin(models.Model):
    __new_guid = None
    __update_guid = None
    __new_guid_text = False

    _guid = GenericRelation(
        to=GUID,
        object_id_field="chat_id",
        content_type_field="chat_content_type",
    )

    __cache_key = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__cache_key = cache.format_key(self.pk, key_name='guid')

    def __clean_guid_attrs(self):
        """set new&update guid attrs to None 
        after saving"""
        self.__new_guid = None
        self.__update_guid = None
        self.__new_guid_text = False

    @property
    def guid(self) -> Optional[str]:
        """Return guid text if exists else None"""
        g_id = cache.get(self.__cache_key, False)
        if g_id == False:
            g_id = None
            guid = self._guid.first()
            if guid:
                g_id = guid.guid

            cache.set(self.__cache_key, g_id)

        return g_id

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

        self.__new_guid_text = new_id

    @guid.deleter
    def guid(self):
        cache.delete(self.__cache_key)
        self._guid.all().delete()

    def save(self, *args, **kwargs):
        with transaction.atomic():
            r = super().save(*args, **kwargs)

            if (g_id := self.__new_guid):
                self._guid.add(g_id, bulk=False)
            elif (g_id := self.__update_guid):
                g_id.save()

            if self.__new_guid_text != False:
                cache.set(self.__cache_key, self.__new_guid_text)
            self.__clean_guid_attrs()

        return r

    class Meta:
        abstract = True
