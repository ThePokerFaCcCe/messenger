from django.db.models.signals import post_save
from django.dispatch import receiver

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from message.models import Message
from message.serializers import MessageSerializer


@receiver(post_save, sender=Message)
def send_message_to_channels(sender, instance: Message,
                             created, **kwargs):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        str(instance.chat_id),
        {
            'type': "event.send_message",
            'event': "receive_message",
            'message': MessageSerializer(instance).data
        }
    )
