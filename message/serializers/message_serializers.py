from copy import deepcopy  # Used for Fix RuntimeError: ...Serializer() cannot be re-used. Create a new instance.
from django.db import transaction
from rest_framework import serializers
from generic_relations.relations import GenericRelatedField

from message.models import Message
from core.utils import count_field
from user.serializers import UserSerializer
from .utils import (MESSAGE_CHAT_GENERICS, MESSAGE_CONTENT_GENERICS,
                    get_content_serializer)


class ForwardedMessageInfoSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'chat_id',
            'sent_at',
            'sender',
        ]


class MessageSerializer(serializers.ModelSerializer):
    chat = GenericRelatedField(deepcopy(MESSAGE_CHAT_GENERICS),
                               read_only=True)
    content = GenericRelatedField(deepcopy(MESSAGE_CONTENT_GENERICS))
    sender = UserSerializer(read_only=True)
    seen_count = serializers.SerializerMethodField()
    forwarded_from = ForwardedMessageInfoSerializer(read_only=True)

    class Meta:
        model = Message
        read_only_fields = [
            'sent_at',
            'is_edited',
            'edited_at',
        ]
        fields = [
            'id',
            'content_type',
            'content',
            'chat',
            'sender',
            'seen_count',
            "forwarded_from",
        ]

    def get_seen_count(self, instance) -> int:
        return count_field(instance, "seen_users")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        content_instance = self.instance.content if self.instance else None
        content_serializer = get_content_serializer(attrs['content_type'],
                                                    data=attrs['content'],
                                                    instance=content_instance)
        content_serializer.is_valid(raise_exception=True)
        attrs['content'] = content_serializer

        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        if(content := self.validated_data.pop('content', None)):
            content = content.save()

            kwargs['content'] = content

        return super().save(**kwargs)


class MessageInfoSerializer(serializers.ModelSerializer):
    content = GenericRelatedField(deepcopy(MESSAGE_CONTENT_GENERICS))
    sender = UserSerializer(read_only=True)
    seen_count = serializers.SerializerMethodField()
    forwarded_from = ForwardedMessageInfoSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'chat_id',
            'content_type',
            'content',
            'sent_at',
            'sender',
            'forwarded_from',
            'seen_count',
        ]

    def get_seen_count(self, instance) -> int:
        return count_field(instance, "seen_users")
