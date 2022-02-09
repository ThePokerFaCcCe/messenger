from rest_framework import serializers

from user.serializers import UserSerializer
from community.models import Member


common_fields = [
    'id',
    "rank",
    "user",
]


class MemberInfoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = common_fields


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = common_fields+[
            "used_guid",
            "used_link",
            "joined_by",
        ]
