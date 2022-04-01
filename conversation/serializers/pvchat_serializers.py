from rest_framework import serializers

from user.serializers import UserInfoSerializer
from conversation.models import PrivateChat


class PrivateChatSerializer(serializers.ModelSerializer):

    creator = UserInfoSerializer(read_only=True)
    user: UserInfoSerializer = serializers.SerializerMethodField()

    class Meta:
        model = PrivateChat
        fields = [
            'user',
            'creator'
        ]

    def get_user(self, pv: PrivateChat):
        if (request := self.context.get('request')):
            self_user = request.user
            if (another := pv.get_reciever_user(self_user)):
                return UserInfoSerializer(another).data
