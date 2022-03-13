from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver, Signal

from core.cache import cache
from core.signals import post_soft_delete
from message.models import Message, DeletedMessage, Seen
from message.serializers import (MessageSerializer, DeletedMessageSerializer,
                                 HardDeletedMessageSerializer, SeenInfoSerializer)
from messenger_channels.utils import send_message_event, send_event


pre_update_message = Signal(providing_args=['instance'])
post_update_message = Signal(providing_args=['instance'])


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
def send_delete_message_to_channels(sender,
                                    instance: DeletedMessage,
                                    created, **kwargs):
    send_message_event(
        group_name=f"user_{instance.user_id}",
        event_title="delete_message",
        message=DeletedMessageSerializer(instance).data
    )


@receiver(post_save, sender=DeletedMessage)
def add_deleted_message_to_cache(sender,
                                 instance: DeletedMessage,
                                 created, **kwargs):

    cache_key = cache.format_key(key_name='deleted_message',
                                 msg_id=instance.message_id,
                                 user_id=instance.user_id)
    cache.set(cache_key, True)


@receiver([post_soft_delete, post_delete], sender=Message)
def send_hard_delete_message_to_channels(sender, instance: Message, **_):
    send_event(
        group_name=instance.chat_id,
        event_title="hard_delete_message",
        event_type='change_in_message',
        message=HardDeletedMessageSerializer(instance).data,
        msg_id=instance.pk,
    )


@receiver(post_update_message, sender=Message)
def send_update_message_to_channels(sender, instance: Message, **_):
    send_event(
        group_name=instance.chat_id,
        event_title="update_message",
        event_type='change_in_message',
        message=MessageSerializer(instance).data,
        msg_id=instance.pk,
    )


@receiver(post_update_message, sender=Message)
def set_message_is_edited(sender, instance: Message, **_):
    if not instance.is_edited:
        instance.is_edited = True
        instance.save()


@receiver(post_save, sender=Seen)
def send_seen_message_to_channels(sender, instance: Seen, created, **_):
    if created:
        send_event(
            group_name=instance.message.chat_id,
            event_title="seen_message",
            event_type='change_in_message',
            message=SeenInfoSerializer(instance).data,
            msg_id=instance.message_id,
        )
