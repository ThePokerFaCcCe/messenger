from typing import Optional, Union
from django.contrib.contenttypes.models import ContentType

from conversation.models import Conversation, PrivateChat
from conversation.querysets import get_or_create_pvchat
from community.models import CommunityChat


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
    pv = get_or_create_pvchat(chat_id, user_id)
    return pv.pk if pv else None
