from rest_framework import serializers

from auth_app.models import Access
from user.serializers import DeviceInfoSerializer


class AccessCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Access
        fields = [
            'token'
        ]
        extra_kwargs = {
            'token': {"source": "encrypted_token",
                      'read_only': True}
        }


class AccessInfoSerializer(serializers.ModelSerializer):
    device = DeviceInfoSerializer()

    class Meta:
        model = Access
        fields = [
            'ip',
            'last_used',
            'device',
        ]
        read_only_fields = fields
