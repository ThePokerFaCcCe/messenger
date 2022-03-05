from typing import Optional
from django.db import transaction

from conversation.models import PrivateChat


def get_or_create_pvchat(creator, receiver) -> Optional[PrivateChat]:
    """Return PrivateChat if receiver was a valid choice"""
    users = [creator, receiver]
    pv = PrivateChat.objects.filter(users=users).first()
    if not pv:
        try:
            with transaction.atomic():
                pv = PrivateChat.objects.create(creator_id=creator)
                pv.users.set(users)
        except Exception as e:
            return None
    return pv
