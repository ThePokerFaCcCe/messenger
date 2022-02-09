from rest_framework import serializers

from community.models import GroupRules


class GroupRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupRules
        fields = [
            'can_send_message',
            'can_add_member',
        ]
