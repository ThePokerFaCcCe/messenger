from typing import Union
from celery import shared_task as task

from conversation.models import Conversation


@task
def create_conversation(chat, user_id):
    Conversation.objects.create(
        chat=chat, user_id=user_id
    )


@task
def create_conversations(chat, user_ids: list):
    """Create conversation of one chat for list of user_ids"""
    users_have_conv = Conversation.objects.only('id').filter(
        chat_id=chat.pk, user_id__in=user_ids
    ).values_list('id', flat=True)
    convs = [
        Conversation(chat=chat, user_id=user_id)
        for user_id in user_ids
        if int(user_id) not in users_have_conv
    ]
    if convs:
        Conversation.objects.bulk_create(convs)


@task
def delete_conversation(chat_id, user_id: Union[str, int, list]):
    filter_kwarg = {}
    if isinstance(user_id, list):
        filter_kwarg['user_id__in'] = user_id
    else:
        filter_kwarg['user_id'] = user_id
    Conversation.objects.filter(
        chat_id=chat_id, **filter_kwarg
    ).delete()
