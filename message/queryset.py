from django.db.models import Q, QuerySet, Count

from core.cache import cache
from .models import Message, DeletedMessage


def get_chat_messages(chat_id, user_id) -> QuerySet:
    """
    returns a queryset of messages that
    isn't deleted by user or others
    """

    deleted_msgs = DeletedMessage.objects.filter(
        message__chat_id=chat_id, user_id=user_id
    ).only('message_id').values_list('message_id')

    return Message.objects.select_related('sender')\
        .prefetch_related('chat', 'content')\
        .annotate(seen_users_count=Count("seen_users"))\
        .filter_not_deleted(
        ~Q(id__in=deleted_msgs),
        chat_id=chat_id,
    )


def delete_message(msg_id, user_id) -> tuple[DeletedMessage, bool]:
    """
    Deletes a message for specified user if not deleted already 
    and returns DeletedMessage instance
    """
    return DeletedMessage.objects.get_or_create(
        user_id=user_id, message_id=msg_id
    )


def is_message_deleted(msg_id, user_id) -> bool:
    """Checks that the `msg_id` is deleted for `user_id`"""
    cache_key = cache.format_key(key_name='deleted_message',
                                 msg_id=msg_id,
                                 user_id=user_id)
    is_deleted = cache.get(cache_key)
    if is_deleted is None:
        is_deleted = DeletedMessage.objects.only('id').filter(
            message_id=msg_id, user_id=user_id).exists()
        cache.set(cache_key, is_deleted)

    return is_deleted
