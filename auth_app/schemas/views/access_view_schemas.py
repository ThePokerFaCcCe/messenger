from rest_framework import serializers


class AccessCreateSchemaSerializer(serializers.Serializer):
    device_token = serializers.CharField(write_only=True)
