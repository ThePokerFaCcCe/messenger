from message import serializers
from message.models import Message, TextContent
from community.models import CommunityChat
from community.serializers import CommunityChatInfoSerializer
from conversation.models import PrivateChat
from conversation.serializers import PrivateChatSerializer


MESSAGE_CHAT_GENERICS = {
    CommunityChat: CommunityChatInfoSerializer(),
    PrivateChat: PrivateChatSerializer(),
}

MESSAGE_CONTENT_GENERICS = {
    TextContent: serializers.TextContentSerializer(),
}


msg_types = Message.ContentTypeChoices
CONTENT_SERIALIZERS = {
    msg_types.TEXT: serializers.TextContentSerializer
}

CONTENT_UPDATE_SERIALIZERS = {
    msg_types.TEXT: serializers.TextContentSerializer
}


def get_content_serializer(content_type: Message.ContentTypeChoices,
                           *serializer_args, **serializer_kwargs):
    serializer = CONTENT_SERIALIZERS.get(content_type, None)

    assert serializer is not None, (
        f"Serializer for type {content_type} is not defined "
    )

    return serializer(*serializer_args, **serializer_kwargs)
