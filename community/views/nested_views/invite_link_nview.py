from django.db.models import Count
from rest_framework import viewsets, mixins

from core.views.mixins import NestedViewMixin
from community.serializers import (InviteLinkMemberInfoSerializer,
                                   InviteLinkInfoSerializer)
from community.models import InviteLink, CommunityChat
from community.permissions import IsCommunityAdminMember


class InviteLinkNestedViewSet(mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.CreateModelMixin,
                              NestedViewMixin,
                              viewsets.GenericViewSet):

    queryset = InviteLink.objects.all()
    nested_queryset = CommunityChat.objects.all()

    nested_lookup_field = 'community_id'

    def get_queryset(self):
        qs = super().get_queryset()

        if self.action == 'destroy':
            return qs.select_for_update()
        else:
            return qs.annotate(
                members_used_count=Count('members_used'))

    def get_permissions(self):
        return [IsCommunityAdminMember()]

    def get_serializer_class(self):
        if self.action == 'create':
            return InviteLinkInfoSerializer

        return InviteLinkMemberInfoSerializer

    def perform_destroy(self, instance: InviteLink):
        instance.soft_delete()

    def perform_create(self, serializer):
        serializer.save(community=self.nested_object)
