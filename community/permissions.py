from typing import Optional
from rest_framework import permissions, views

from community.models import Member


def get_member(request, view) -> Optional[Member]:
    user_id = request.user.pk
    if isinstance(view, views.APIView):
        cid_lookup_url = getattr(
            view, 'nested_lookup_field',
            getattr(view, 'lookup_url_kwarg', None)
            or
            getattr(view, 'lookup_field')
        )
        community_id = view.kwargs.get(cid_lookup_url)
    else:
        # Probably the view is a Consumer object
        community_lookup = getattr(view, 'community_query_lookup', 'chat_id')
        community_id = request.query.get(community_lookup)

    return Member.objects.filter(
        community_id=community_id, user_id=user_id
    ).first()


class MemberRankPermissionMixin(permissions.IsAuthenticated):
    def check_rank(self, rank) -> bool: raise NotImplementedError()

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            member = get_member(request, view)
            return member and self.check_rank(member.rank)


class IsCommunityOwnerMember(MemberRankPermissionMixin):
    def check_rank(self, rank) -> bool:
        return rank == Member.RankChoices.OWNER

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsCommunityAdminMember(MemberRankPermissionMixin):
    def check_rank(self, rank) -> bool:
        return rank >= Member.RankChoices.ADMIN

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsCommunityNormalMember(MemberRankPermissionMixin):
    def check_rank(self, rank) -> bool:
        return rank >= Member.RankChoices.NORMAL


class IsCommunityMember(MemberRankPermissionMixin):
    def check_rank(self, rank) -> bool:
        return rank >= Member.RankChoices.RESTRICTED


class IsNotCommunitySelfMember(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: Member):
        return request.user != obj.user


class HasHigherRankThanMember(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: Member):
        return get_member(request, view).rank > obj.rank
