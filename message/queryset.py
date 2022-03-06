from django.db.models.expressions import Q
from message.models import Message, DeletedMessage


def get_chat_messages(chat_id, user_id):
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
