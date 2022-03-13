from rest_framework import serializers
from generic_relations.relations import GenericRelatedField

from core.utils import count_field
from picturic.serializer_fields import PictureField
from community.models import CommunityChat, GroupCommunity
from user.serializers import UserSerializer
import community.serializers.group_serializers as gp_serializers


class CommunityChatSerializer(serializers.ModelSerializer):
    community = GenericRelatedField({
        GroupCommunity: gp_serializers.GroupCommunitySerializer()
    }, read_only=True)
    creator = UserSerializer(read_only=True)
    profile_image = PictureField(read_only=True)
    members_count = serializers.SerializerMethodField()

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
            'members_count'
        ] + read_only_fields

    def get_members_count(self, instance) -> int:
        return count_field(instance, 'members')

    def create(self, validated_data):
        ctype = validated_data.get('type')
        creator = self.context.get('request').user
        community = None
        if ctype == CommunityChat.TypeChoices.GROUP:
            community = GroupCommunity.objects.create()
        return super().create(
            validated_data | {'community': community,
                              'creator': creator})


class CommunityChatInfoSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    profile_image = PictureField(read_only=True)

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


class CommunityChatUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityChat
        fields = [
            'id',
            'name',
            'description',
        ]
