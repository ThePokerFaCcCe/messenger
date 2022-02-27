# from message.serializers.message_serializers import MessageSerializer as ms;m=ms(data={'content_type':'text','content':{'text':'hellob'}});m.is_valid(raise_exception=True)
from django.db import transaction
from rest_framework import serializers
from generic_relations.relations import GenericRelatedField

from message.models import Message

from user.serializers import UserSerializer
from .utils import (MESSAGE_CHAT_GENERICS, MESSAGE_CONTENT_GENERICS,
                    get_content_serializer)


class MessageSerializer(serializers.ModelSerializer):
    chat = GenericRelatedField(MESSAGE_CHAT_GENERICS,
                               read_only=True)
    content = GenericRelatedField(MESSAGE_CONTENT_GENERICS)
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        read_only_fields = [
            'is_edited',
            'edited_at',
        ]
        fields = [
            'id',
            'content_type',
            'content',
            'chat',
            'sender',
        ]

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
