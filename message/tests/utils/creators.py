from message.models import Message, DeletedMessage, TextContent

from user.tests.utils import create_active_user
from conversation.tests.utils import create_private_chat


def create_text_content(text='hello') -> TextContent:
    return TextContent.objects.create(text=text)


def create_message(sender=None, chat=None, content=None,
                   content_type=Message.ContentTypeChoices.TEXT
                   ) -> Message:
    sender = sender if sender else create_active_user()
    data = {
        'sender': sender,
        'chat': chat if chat else create_private_chat(sender),
        'content': content if content else create_text_content(),
        'content_type': content_type,
    }

    return Message.objects.create(**data)


def create_deleted_msg(msg=None, user=None) -> DeletedMessage:
    user = create_active_user() if not user else user

    return DeletedMessage.objects.create(
        message=msg if msg else create_message(sender=user),
        user=user)
