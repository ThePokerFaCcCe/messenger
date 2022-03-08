from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

layer = get_channel_layer()


def send_message_event(group_name, event_title, **data):
    """
    Calls `event_send_message` method of channels
    that joined in `group_name`
    """
    async_to_sync(layer.group_send)(
        str(group_name),
        {
            'type': "event.send_message",
            'event': event_title,
            **data
        }
    )
