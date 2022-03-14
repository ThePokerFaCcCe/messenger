from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from core.cache import cache
from messenger_channels.querysets import get_pvchat_ids
from conversation.models import PrivateChat


@receiver(m2m_changed, sender=PrivateChat.users.through)
def add_new_conv_for_consumers(sender, instance: PrivateChat,
                               action, **kwargs):
    if action == 'post_add':
        user_ids = kwargs['pk_set']
        layer = get_channel_layer()
        for user_id in user_ids:
            user_group = f'user_{user_id}'
            async_to_sync(layer.group_send)(
                user_group,
                {
                    'type': "event.group_join",
                    'group_name': str(instance.pk)
                }
            )

            # Update cached pvchats
            cache.set(
                cache.format_key(user_id, key_name='user_pvs'),
                get_pvchat_ids(user_id)
            )
