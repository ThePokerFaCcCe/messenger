from rest_framework import serializers

from user.models import Device


class DeviceCreateSchemaSerializer(serializers.ModelSerializer):
    verifycode_token = serializers.CharField(write_only=True)

    class Meta:
        model = Device
        fields = [
            "verifycode_token",
            "type",
            "model",
            "token",
        ]
        extra_kwargs = {
            'token': {"read_only": True, "source": "encrypted_token"}
        }
