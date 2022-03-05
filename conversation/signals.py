from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from core.utils import delete_instance_on_error
from conversation.tasks import create_conversations
from conversation.models import PrivateChat


@receiver(m2m_changed, sender=PrivateChat.users.through)
def create_member_conversation(sender, instance: PrivateChat,
                               action, **kwargs):
    if action == 'post_add':
        delete_instance_on_error(
            create_conversations, instance=instance,
            chat=instance,
            user_ids=kwargs['pk_set']
        )
