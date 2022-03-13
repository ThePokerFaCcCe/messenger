from rest_framework import serializers

from message.models import Seen
from user.serializers import UserSerializer


class SeenUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Seen
        fields = [
            'user',
            'message_id',
            'seen_at'
        ]
