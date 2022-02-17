from django.db import transaction
from rest_framework import viewsets, response, status
from rest_framework.decorators import action

from community.models import Member
from community.permissions import IsCommunityMember


class CommunityLeaveMixin(viewsets.GenericViewSet):
    def get_permissions(self):
        if self.action == 'leave':
            return [IsCommunityMember()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'leave':
            return None
        return super().get_serializer_class()

    def get_member(self) -> Member:
        """Returns member object"""
        comm = self.get_object()
        return Member.objects.filter(
            community=comm,
            user=self.request.user
        ).first()

    @action(['post'], detail=True)
    def leave(self, request, *args, **kwargs):
        """Leave to community, if member were owner,
        the community *will be deleted* too"""

        member = self.get_member()
        with transaction.atomic():
            # Because of post_delete signals
            member.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
