from django.db.models.manager import BaseManager

from ..queryset.conversation_queryset import ConversationQuerySet


class ConversationManager(
        BaseManager.from_queryset(
            ConversationQuerySet
        )):
    pass
