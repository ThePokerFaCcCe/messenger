from celery import shared_task as task

from conversation.models import Conversation


@task
def create_conversation(chat, user_id):
    Conversation.objects.create(
        chat=chat, user_id=user_id
    )
