from rest_framework import serializers
from generic_relations.relations import GenericRelatedField

from community.models import CommunityChat, GroupCommunity
from user.serializers import UserSerializer
import community.serializers.group_serializers as gp_serializers


def count_members(instance: CommunityChat) -> int:
    count = getattr(instance, 'members_count', None)
    if count is None:
        count = instance.objects.members.count()
    return count


class CommunityChatSerializer(serializers.ModelSerializer):
    community = GenericRelatedField({
        GroupCommunity: gp_serializers.GroupCommunitySerializer()
    })
    creator = UserSerializer()
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = CommunityChat

        read_only_fields = [
            'profile_image',
            'creator',
            'community',
            'members_count'
            'created_at'
        ]

        fields = [
            'id',
            'type',
            'name',
            'description',
        ] + read_only_fields

    def get_members_count(self, instance) -> int:
        return count_members(instance)


class CommunityChatInfoSerializer(serializers.ModelSerializer):
    creator = UserSerializer()

    class Meta:
        model = CommunityChat
        fields = [
            'id',
            'type',
            'name',
            'description',
            'profile_image',
            'creator',
            'created_at'
        ]
