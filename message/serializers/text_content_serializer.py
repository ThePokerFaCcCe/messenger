from rest_framework import serializers

from message.models import TextContent


class TextContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextContent
        fields = [
            'text'
        ]
