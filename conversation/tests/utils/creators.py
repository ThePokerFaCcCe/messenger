from conversation.models import Conversation, PrivateChat
from user.tests.utils import create_active_user


def create_private_chat(creator=None, receiver=None, **kwargs
                        ) -> PrivateChat:
    creator = creator if creator else create_active_user()
    receiver = receiver if receiver else create_active_user()

    pv = PrivateChat.objects.create(creator=creator,
                                    **kwargs)
    pv.users.set([creator, receiver])

    return pv


def create_conversation(chat=None, user=None, **kwargs) -> Conversation:
    user = create_active_user() if not user else user
    chat = chat if chat else create_private_chat(creator=user)

    return Conversation.objects.create(
        chat=chat, user=user, **kwargs)
