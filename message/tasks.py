from .models import Message


def forward_message(instance: Message, chat_id, sender):
    """
    Create new message model & add `instance` 
    to it's forwarded_from FK
    """

    new_msg = Message()
    new_msg.content = instance.content
    new_msg.content_type = instance.content_type
    new_msg.forwarded_from = instance
    new_msg.sender = sender
    new_msg.chat_id = chat_id

    new_msg.save()
    return new_msg
