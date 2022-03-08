from rest_framework import serializers

from message.models import DeletedMessage, Message


class DeletedMessageSerializer(serializers.ModelSerializer):
    chat_id = serializers.SerializerMethodField()

    class Meta:
        model = DeletedMessage

        fields = [
            'chat_id',
            'message_id',
            'user_id',
        ]

    def get_chat_id(self, instance: DeletedMessage) -> int:
        return instance.message.chat_id


class HardDeletedMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message

        fields = [
            'chat_id',
            'message_id',
        ]

        extra_kwargs = {
            'message_id': {'source': "id"}
        }
