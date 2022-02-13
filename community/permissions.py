from typing import Optional
from rest_framework import permissions

from community.models import Member


def get_member(request, view) -> Optional[Member]:
    user_id = request.user.pk

    cid_lookup_url = getattr(
        view, 'nested_lookup_field',
        getattr(view, 'lookup_url_kwarg', None)
        or
        getattr(view, 'lookup_field')
    )
    community_id = view.kwargs.get(cid_lookup_url)

    return Member.objects.filter(
        community_id=community_id, user_id=user_id
    ).first()


class IsCommunityOwnerMember(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            member = get_member(request, view)
            return member and member.rank == Member.RankChoices.OWNER


class IsCommunityAdminMember(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            member = get_member(request, view)
            return member and member.rank >= Member.RankChoices.ADMIN


class IsCommunityNormalMember(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            member = get_member(request, view)
            return member and member.rank >= Member.RankChoices.NORMAL
