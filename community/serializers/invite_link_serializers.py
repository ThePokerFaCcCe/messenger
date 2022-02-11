from rest_framework import serializers

from community.models import InviteLink
import community.serializers.member_serializers as member_serializers
import community.serializers.community_serializers as community_serializers

common_fields = [
    'id',
    'link',
    'is_deleted',
    'created_at',
    'deleted_at',
]


class InviteLinkInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteLink
        fields = common_fields


class InviteLinkSerializer(serializers.ModelSerializer):
    members_used = member_serializers\
        .MemberInfoSerializer(many=True, read_only=True)
    chat = community_serializers\
        .CommunityChatInfoSerializer(read_only=True)

    class Meta:
        model = InviteLink
        fields = common_fields + [
            'chat',
            "members_used",
        ]


class InviteLinkMemberInfoSerializer(serializers.ModelSerializer):
    members_used = member_serializers\
        .MemberInfoSerializer(many=True, read_only=True)

    class Meta:
        model = InviteLink
        fields = common_fields + [
            "members_used",
        ]
