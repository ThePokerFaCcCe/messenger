from rest_framework import serializers
from generic_relations.relations import GenericRelatedField

from community.models import CommunityChat
from community.serializers import CommunityChatInfoSerializer
from conversation.models import Conversation, PrivateChat
from .pvchat_serializers import PrivateChatSerializer


class ConversationSerializer(serializers.ModelSerializer):
    chat = GenericRelatedField({
        PrivateChat: PrivateChatSerializer(),
        CommunityChat: CommunityChatInfoSerializer(),
    }, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id',
            "type",
            "alias",
            "is_pinned",
            "is_archived",
            "chat",
        ]

        extra_kwargs = {
            'chat': {"read_only": True}
        }


class ConversationPinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            'id',
            "is_pinned",
        ]
        read_only_fields = fields


class ConversationArchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            'id',
            "is_archived",
        ]
        read_only_fields = fields


class ConversationAliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            'id',
            "alias",
        ]


class ConversationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            'id',
            "alias",
            "is_archived",
            "is_pinned",
        ]
