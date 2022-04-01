from rest_framework import serializers

from message.models import Seen
from user.serializers import UserInfoSerializer


class SeenUserSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)

    class Meta:
        model = Seen
        fields = [
            'user',
            'message_id',
            'seen_at'
        ]


class SeenInfoSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)
    chat_id = serializers.SerializerMethodField()

    class Meta:
        model = Seen
        fields = [
            'user',
            'chat_id',
            'message_id',
            'seen_at'
        ]

    def get_chat_id(self, instance: Seen) -> int:
        return instance.message.chat_id
