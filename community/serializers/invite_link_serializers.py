from rest_framework import serializers

from core.utils import count_field
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
        read_only_fields = fields


class InviteLinkSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    community = community_serializers\
        .CommunityChatInfoSerializer(read_only=True)

    class Meta:
        model = InviteLink
        fields = common_fields + [
            'community',
            "members_count",
        ]

    def get_members_count(self, instance) -> int:
        return count_field(instance, 'members_used')


class InviteLinkMemberInfoSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = InviteLink
        fields = common_fields + [
            "members_count",
        ]

    def get_members_count(self, instance) -> int:
        return count_field(instance, 'members_used')
