from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
# Only post_delete signal will be called on both queryset or instance `delete` methods

from core.cache import cache
from .models import GUID


@receiver([post_save, post_delete], sender=GUID)
def update_guid_cache(sender, instance: GUID, **kwargs):
    key = cache.format_key(instance.chat_id, key_name="guid")
    if 'created' in kwargs.keys() and instance.pk:
        cache.set(key, instance.guid)
    else:
        cache.delete(key)
