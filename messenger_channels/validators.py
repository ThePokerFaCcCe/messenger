from typing import Any

from .querysets import get_validated_chat_id


def validate_chat_id(chat_id, consumer) -> tuple[bool, Any]:
    """
    validator that used for consumer query params
    """
    chat_id = get_validated_chat_id(chat_id, consumer.scope.user.id)
    if chat_id is None or str(chat_id) not in consumer.groups:
        return (False, "Not found")
    return (True, chat_id)
