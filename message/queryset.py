from django.db.models import Q, QuerySet
from message.models import Message, DeletedMessage


def get_chat_messages(chat_id, user_id) -> QuerySet:
    """
    returns a queryset of messages that
    isn't deleted by user or others
    """

    deleted_msgs = DeletedMessage.objects.filter(
        message__chat_id=chat_id, user_id=user_id
    ).only('message_id').values_list('message_id')

    return Message.objects.filter_not_deleted(
        ~Q(id__in=deleted_msgs),
        chat_id=chat_id,
    )


def delete_message(msg_id, user_id) -> DeletedMessage:
    """
    deletes a message for specified user and
    returns DeletedMessage instance
    """
    return DeletedMessage.objects.create(
        user_id=user_id, message_id=msg_id
    )
