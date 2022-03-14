from django.dispatch import receiver
from django.contrib.auth import get_user_model
from messenger_channels.querysets import get_pvchat_ids_cached

from user.signals import user_online
from user.serializers import UserLastSeenSerializer
from messenger_channels.utils import send_event

User = get_user_model()


@receiver(user_online, sender=User)
def send_user_online_to_channels(sender, instance, **_):
    pv_ids = get_pvchat_ids_cached(instance.pk)

    for pv_id in pv_ids:
        send_event(
            group_name=pv_id,
            event_title="user_online",
            event_type='send_online',
            user=UserLastSeenSerializer(instance).data,
        )
