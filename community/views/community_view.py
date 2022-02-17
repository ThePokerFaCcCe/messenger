from django.db.models import Count
from rest_framework import viewsets, mixins, permissions

from community.permissions import IsCommunityAdminMember, IsCommunityNormalMember
from community.models import CommunityChat
from community.serializers import (CommunityChatSerializer,
                                   CommunityChatUpdateSerializer)
from .mixins import CommunityJoinMixin, CommunityLeaveMixin


class CommunityChatViewSet(mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.CreateModelMixin,
                           CommunityJoinMixin,
                           CommunityLeaveMixin,
                           viewsets.GenericViewSet):
    queryset = CommunityChat.objects.all()
    serializer_class = CommunityChatSerializer
    permission_classes = [IsCommunityNormalMember]
    lookup_field = 'id'

    def get_queryset(self):
        qs = super().get_queryset()

        if self.action in ['get', 'retrieve']:
            return qs.select_related("creator")\
                .prefetch_related('community__rules')\
                .annotate(members_count=Count('members'))

        return qs.select_for_update()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CommunityChatUpdateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsCommunityAdminMember()]
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def perform_destroy(self, instance):
        instance.soft_delete()
