from typing import Optional, Union
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

from conversation.models import Conversation, PrivateChat
from conversation.querysets import get_or_create_pvchat
from community.models import CommunityChat

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def get_chat_ids(user_id) -> set:
    """Return list of chat ids inside of user conversations"""
    return set(
        Conversation.objects
        .only('chat_id')
        .filter(user_id=user_id)
        .values_list('chat_id', flat=True)
    )


def get_chat_content_type(chat_id: Union[int, str]) -> ContentType:
    """Return chat's content type from `chat_id`"""
    if int(chat_id) > 0:
        return ContentType.objects.get_for_model(PrivateChat)
    return ContentType.objects.get_for_model(CommunityChat)


def get_validated_chat_id(chat_id, user_id) -> Optional[int]:
    """
    `chat_id` > 0, means that the client sent an user id as `chat_id`,
    so it's PrivateChat id should be returned. if `chat_id` wasn't 
    a valid user, `None` will be returned.
    """
    if chat_id < 0:
        return chat_id

    cache_key = f'pv_{chat_id}_{user_id}'
    cache_key = cache_key if cache_key in cache else f'pv_{user_id}_{chat_id}'
    pv_id = cache.get(cache_key)

    if not pv_id:
        pv = get_or_create_pvchat(user_id, chat_id)
        if not pv:
            return
        pv_id = pv.pk
        cache.set(cache_key, pv_id, timeout=CACHE_TTL)

    return pv_id
