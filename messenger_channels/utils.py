from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

layer = get_channel_layer()


def send_event(group_name, event_title: str,
               event_type: str, **data):
    '''
    Calls `event_type` method of channels in `group_name`

    PS: "event." will add to `event_type` if not exists.
    e.g. "send" -> "event.send"
    '''
    event_type = (event_type
                  if event_type.lower().startswith('event')
                  else f"event.{event_type}")
    async_to_sync(layer.group_send)(
        str(group_name),
        {
            'type': event_type,
            'event': event_title,
            **data
        }
    )


def send_message_event(group_name, event_title: str, **data):
    """
    Calls `event_send_message` method of channels in `group_name`
    """
    send_event(group_name, event_title,
               event_type="send_message", **data)
