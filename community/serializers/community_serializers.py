from rest_framework import serializers
from generic_relations.relations import GenericRelatedField

from community.models import CommunityChat, GroupCommunity
from user.serializers import UserSerializer
import community.serializers.group_serializers as gp_serializers


class CommunityChatSerializer(serializers.ModelSerializer):
    community = GenericRelatedField({
        GroupCommunity: gp_serializers.GroupCommunitySerializer()
    })
    creator = UserSerializer()

    class Meta:
        model = CommunityChat

        read_only_fields = [
            'profile_image',
            'creator',
            'community',
            'created_at'
        ]

        fields = [
            'id',
            'type',
            'name',
            'description',
        ] + read_only_fields


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
