from typing import Union
from django.contrib.contenttypes.models import ContentType

from conversation.models import PrivateChat
from community.models import CommunityChat


def get_chat_content_type(chat_id: Union[int, str]) -> ContentType:
    """Return chat's content type from `chat_id`"""
    if int(chat_id) > 0:
        return ContentType.objects.get_for_model(PrivateChat)
    return ContentType.objects.get_for_model(CommunityChat)
