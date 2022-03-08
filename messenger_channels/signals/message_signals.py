from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from core.signals import post_soft_delete
from message.models import Message, DeletedMessage
from message.serializers import MessageSerializer, DeletedMessageSerializer, HardDeletedMessageSerializer
from messenger_channels.utils import send_message_event


@receiver(post_save, sender=Message)
def send_message_to_channels(sender, instance: Message,
                             created, **kwargs):
    if created:
        send_message_event(
            group_name=instance.chat_id,
            event_title="receive_message",
            message=MessageSerializer(instance).data
        )


@receiver(post_save, sender=DeletedMessage)
def send_delete_message_from_channels(sender,
                                      instance: DeletedMessage,
                                      created, **kwargs):
    send_message_event(
        group_name=f"user_{instance.user_id}",
        event_title="delete_message",
        message=DeletedMessageSerializer(instance).data
    )


@receiver([post_soft_delete, post_delete], sender=Message)
def send_hard_delete_message_from_channels(sender, instance: Message,
                                           **kwargs):
    send_message_event(
        group_name=instance.chat_id,
        event_title="hard_delete_message",
        message=HardDeletedMessageSerializer(instance).data
    )
