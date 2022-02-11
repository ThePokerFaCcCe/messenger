from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action

from core.views.mixins import NestedViewMixin
from community.serializers import MemberSerializer, MemberUpdateSerializer
from community.models import Member
from community.permissions import IsCommunityAdminMember, IsCommunityNormalMember


class MemberNestedViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        NestedViewMixin,
        viewsets.GenericViewSet):

    queryset = Member.objects.all()

    nested_lookup_field = 'community_id'

    lookup_field = 'user_id'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        qs = super().get_queryset()

        if self.action in ['list', 'retrieve']:
            return qs.select_related('user', '_used_link')
        else:
            return qs.select_for_update()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return MemberUpdateSerializer
        return MemberSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'ban']:
            return [IsCommunityAdminMember()]
        return [IsCommunityNormalMember()]

    @action(['post'], detail=True)
    def ban(self, *args, **kwargs):
        member = self.get_object()
        member.rank = Member.RankChoices.BANNED
        member.save()
        return Response(status=status.HTTP_200_OK)
