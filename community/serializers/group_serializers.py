from rest_framework import serializers

from community.models import GroupCommunity
from community.serializers import GroupRulesSerializer


class GroupCommunitySerializer(serializers.ModelSerializer):
    rules = GroupRulesSerializer(read_only=True)

    class Meta:
        model = GroupCommunity
        fields = [
            'rules'
        ]
