from rest_framework import serializers

from user.models import Device


class DeviceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            "type",
            "model",
            "token",
        ]
        extra_kwargs = {
            'token': {"read_only": True, "source": "encrypted_token"}
        }


class DeviceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            "type",
            "model",
        ]
