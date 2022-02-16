from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from core.utils import get_field_attr
from community.models import InviteLink, Member, CommunityChat
from global_id.models import GUID


class JoinCommunitySerializer(serializers.Serializer):
    default_error_messages = {
        'only_one': _('you should fill only one field'),
        '404_link': _("Entered invite link is expired or doesn't exists"),
        '404_guid': _("Entered guid not found"),
        'bad_guid': _("Entered guid is not valid"),
        'banned_member': _("{ctype} isn't accessible"),
        'already_joined': _("You're already joined in this {ctype}"),
    }
    guid = serializers.CharField(
        validators=get_field_attr(GUID, "guid", "validators"),
        allow_null=True, required=False, write_only=True)
    invite_link = serializers.CharField(
        validators=get_field_attr(InviteLink, "link", "validators"),
        allow_null=True, required=False, write_only=True)

    join_data = serializers.HiddenField(default={})
    community = serializers.HiddenField(default=None)
    user = serializers.HiddenField(default=None)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        join_data = attrs['join_data']
        community = None

        guid = attrs.pop('guid', None)
        link = attrs.pop('invite_link', None)

        if all([guid, link]) or not any([guid, link]):
            self.fail('only_one')

        if link:
            found_link = InviteLink.objects\
                .select_related('community')\
                .filter_not_deleted(link=link).first()

            if not found_link:
                self.fail('404_link')

            join_data['_used_link'] = found_link
            community = found_link.community

        elif guid:
            found_guid = GUID.objects.prefetch_related('chat')\
                .filter(guid=guid).first()
            if not found_guid:
                self.fail('404_guid')

            if (getattr(found_guid.chat, 'type', None)
                        not in CommunityChat.TypeChoices.values
                    ):
                self.fail('bad_guid')

            join_data['used_guid'] = found_guid.guid
            community = found_guid.chat

        attrs['community'] = community
        attrs['user'] = getattr(self.context.get('request'), 'user', None)
        return attrs

    def create(self, validated_data):
        join_data = validated_data.pop('join_data', {})
        member, created = Member.objects.get_or_create(
            **validated_data, defaults=join_data)
        if created:
            return member

        comm = validated_data.get('community')
        ctype = dict(CommunityChat.TypeChoices.choices)[comm.type]
        if member.rank == Member.RankChoices.BANNED:
            self.fail("banned_member", ctype=ctype)
        self.fail("already_joined", ctype=ctype)

# from community.serializers import JoinCommunitySerializer as js
# j = js(data={'guid': 'ssssss', 'link': '-ssssssss'})
# j.is_valid(raise_exception=True)
