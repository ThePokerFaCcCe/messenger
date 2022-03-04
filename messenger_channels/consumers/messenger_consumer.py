from generic_channels.consumers import GenericConsumer
from generic_channels.decorators import options
from generic_channels.permissions import IsAuthenticated

from message.serializers import MessageSerializer
from ..querysets import (get_chat_ids, get_chat_content_type,
                         get_validated_chat_id)


class MessengerConsumer(GenericConsumer):
    permission_classes = [IsAuthenticated]

    def connect(self):
        super().connect()
        self.groups_join(get_chat_ids(self.scope.user))

    @options(query_params={"chat_id": {'type': int, 'regex': '^-?\d+$'}})
    def action_send_message(self, content, action, *args, **kwargs):
        chat_id = get_validated_chat_id(content.query.chat_id,
                                        self.scope.user.pk)
        if str(chat_id) not in self.groups:
            self.fail('404', item="Chat")

        serializer = self.get_serializer(
            action, content, data=content.body)
        self.validate_serializer(serializer, action)

        serializer.save(
            chat_id=chat_id,
            chat_content_type=get_chat_content_type(chat_id),
            sender=self.scope.user,
        )

        self.success(content, serializer.data)

    def get_serializer_class(self, action, content):
        if action == 'send_message':
            return MessageSerializer
        return super().get_serializer_class(action, content)
