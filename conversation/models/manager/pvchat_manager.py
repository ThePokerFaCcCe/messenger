from django.db.models.manager import BaseManager

from ..queryset import PrivateChatQuerySet


class PrivateChatManager(
        BaseManager.from_queryset(
            PrivateChatQuerySet
        )):
    pass
