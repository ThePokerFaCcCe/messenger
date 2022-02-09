from community.models import (CommunityChat, GroupCommunity, Member,
                              InviteLink, GroupRules)
from user.tests.utils import create_active_user

RANKS = Member.RankChoices


def create_community_chat(community=None, creator=None,
                          **kwargs) -> CommunityChat:
    return CommunityChat.objects.create(
        name='test',
        community=community or create_group_community(),
        creator=creator or create_active_user()
    )


def create_group_community(**kwargs) -> GroupCommunity:
    return GroupCommunity.objects.create(**kwargs)


def create_member(community_chat: CommunityChat = None,
                  user=None, rank: RANKS = RANKS.NORMAL,
                  **kwargs) -> Member:
    return Member.objects.create(
        user=user or create_active_user(),
        community=community_chat
        or create_community_chat(),
        rank=rank, **kwargs
    )


def create_invite_link(chat: CommunityChat = None,
                       **kwargs) -> InviteLink:
    return InviteLink.objects.create(
        chat=chat or create_community_chat()
    )
