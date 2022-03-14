from typing import Optional, Union
from django.contrib.contenttypes.models import ContentType

from core.cache import cache
from conversation.models import Conversation, PrivateChat
from conversation.querysets import get_or_create_pvchat
from community.models import CommunityChat


def get_pvchat_ids(user_id) -> set:
    """Return list of pv ids that contains `user_id`"""

    return set(
        PrivateChat.objects.only('id')
        .filter(users=user_id)
        .values_list('id', flat=True)
    )


def get_pvchat_ids_cached(user_id) -> set:
    """Return cached pvchat ids for `user_id`"""
    key = cache.format_key(user_id, key_name="user_pvs")
    return cache.get_or_set(
        key, default_func=get_pvchat_ids, user_id=user_id
    )


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

    cache_key = cache.format_key(chat_id, user_id, key_name='pv_id')
    if cache_key not in cache._cache:
        cache_key = cache.format_key(user_id, chat_id, key_name='pv_id')

    pv_id = cache.get(cache_key)

    if not pv_id:
        pv = get_or_create_pvchat(user_id, chat_id)
        if not pv:
            return
        pv_id = pv.pk
        cache.set(cache_key, pv_id)

    return pv_id
