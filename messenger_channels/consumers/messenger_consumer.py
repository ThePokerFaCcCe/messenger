from generic_channels.consumers import GenericConsumer
from generic_channels.decorators import options
from generic_channels.permissions import IsAuthenticated

from core.permissions import IsOwnerOfItem
from community.permissions import IsCommunityAdminMember
from message.models import Message
from message.serializers import MessageSerializer, DeletedMessageSerializer
from message.serializers.utils import CONTENT_UPDATE_SERIALIZERS
from message.queryset import delete_message
from ..querysets import (get_chat_ids, get_chat_content_type)
from ..validators import validate_chat_id
from ..signals import pre_update_message, post_update_message

CHATID_PARAM = {
    "chat_id":
        {
            'type': int, 'regex': '^-?\d+$',
            'validator': validate_chat_id,
        }
}


class MessengerConsumer(GenericConsumer):
    default_error_messages = {
        'cant_update': "can't update this message"
    }
    permission_classes = [IsAuthenticated]

    def connect(self):
        super().connect()
        self.groups_join(get_chat_ids(self.scope.user))
        self.group_join(f'user_{self.scope.user.pk}')

    @options(query_params=CHATID_PARAM)
    def action_send_message(self, content, action, *args, **kwargs):
        """
        Create message for chat.

        BUG:
        - first message for new privatechats won't send because
          the chat_id isn't still in groups list.
        """
        chat_id = content.query.chat_id

        serializer = self.get_serializer(
            action, content, data=content.body)
        self.validate_serializer(serializer, action)

        serializer.save(
            chat_id=chat_id,
            chat_content_type=get_chat_content_type(chat_id),
            sender=self.scope.user,
        )

        self.success(content, serializer.data)

    @options(query_params={
        "message_id": {
            'type': int,
            'queryset': Message.objects.filter_not_deleted(),
            'depends': ['chat_id']
        },
        **CHATID_PARAM
    })
    def action_delete_message(self, content, action, *args, **kwargs):
        '''
        Delete message for an user.

        if {"hard":True} was in body, the message will be deleted for all users
        '''
        msg: Message = content.query.message_id_object
        if content.body.get('hard', False):
            msg.soft_delete()
        else:
            delete_message(msg.pk, self.scope.user.pk)

        self.success(content)

    @options(query_params={
        "message_id": {
            'type': int,
            'queryset': Message.objects.select_related('sender')
            .prefetch_related('content', 'chat').filter_not_deleted(),
            'depends': ['chat_id']
        },
        **CHATID_PARAM
    })
    def action_update_message(self, content, action, *args, **kwargs):
        """
        Update message content that user sent.
        """
        msg: Message = content.query.message_id_object

        serializer = self.get_serializer(
            action, content, instance=msg.content,
            data=content.body)
        self.validate_serializer(serializer, action)

        pre_update_message.send(msg.__class__, instance=msg)
        serializer.save()
        post_update_message.send(msg.__class__, instance=msg)

        self.success(content, serializer.data)

    def get_serializer_class(self, action, content):
        if action == 'send_message':
            return MessageSerializer
        if action == 'delete_message':
            return DeletedMessageSerializer
        if action == 'update_message':
            msg: Message = content.query.message_id_object
            serializer = CONTENT_UPDATE_SERIALIZERS.get(msg.content_type)
            if not serializer:
                self.fail('cant_update', action=action)
            return serializer
        return super().get_serializer_class(action, content)

    def get_permissions(self, action: str, content: dict):
        if action == 'delete_message' and content.body.get('hard', False):
            if content.query.chat_id < 0:
                # It's used for Member permission
                self.community_query_lookup = 'chat_id'
                return [(IsCommunityAdminMember | IsOwnerOfItem)()]
            return [IsOwnerOfItem()]
        if action == 'update_message':
            return [IsOwnerOfItem()]
        return super().get_permissions(action, content)
