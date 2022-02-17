from typing import Union
from celery import shared_task as task

from conversation.models import Conversation


@task
def create_conversation(chat, user_id):
    Conversation.objects.create(
        chat=chat, user_id=user_id
    )


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
