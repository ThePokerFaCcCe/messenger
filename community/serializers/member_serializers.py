from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from user.serializers import UserInfoSerializer
from community.models import Member


common_fields = [
    "rank",
    "user",
]


class MemberInfoSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)

    class Meta:
        model = Member
        fields = common_fields


class MemberSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)

    class Meta:
        model = Member
        fields = common_fields+[
            "used_guid",
            "used_link",
            "joined_by",
        ]


class MemberUpdateSerializer(serializers.ModelSerializer):
    default_error_messages = {
        'owner_rank': _("You cannot set Owner rank to member")
    }

    class Meta:
        model = Member
        fields = ['rank']

    def validate_rank(self, rank):
        if rank == Member.RankChoices.OWNER:
            self.fail('owner_rank')
        return rank
