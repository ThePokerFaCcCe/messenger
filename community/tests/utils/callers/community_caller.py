from django.urls.base import reverse, reverse_lazy
from rest_framework import status
from community.models.member import Member

from community.urls import app_name
from community.models import CommunityChat
from core.tests.utils import BaseCaller
from ..creators import create_community_chat, create_invite_link, create_member

COMM_TYPES = CommunityChat.TypeChoices
COMM_LIST_URL = reverse_lazy(f"{app_name}:community-list")

name_nested = f"{app_name}:community-"


def comm_detail_url(pk=None, creator=None):
    return reverse(f"{app_name}:community-detail", kwargs={
        'id': pk or create_community_chat(creator=creator).pk
    })


def get_nested_community(community=None):
    community = community or create_community_chat()
    return community, {'community_id': community.pk}


def invite_detail_url(pk=None, community=None):
    community, ckwargs = get_nested_community(community)
    return reverse(name_nested+"invite-link-detail",
                   kwargs=ckwargs | {
                       'pk': pk or create_invite_link(community).pk,
                   })


def invite_list_url(community=None):
    community, ckwargs = get_nested_community(community)
    return reverse(name_nested+"invite-link-list", kwargs=ckwargs)


def member_detail_url(pk=None, community=None):
    community, ckwargs = get_nested_community(community)
    return reverse(name_nested+"member-detail",
                   kwargs=ckwargs | {
                       'id': pk or create_member(community).pk,
                   })


def member_ban_url(pk=None, community=None):
    community, ckwargs = get_nested_community(community)
    return reverse(name_nested+"member-ban",
                   kwargs=ckwargs | {
                       'id': pk or create_member(community).pk,
                   })


def member_list_url(community=None):
    community, ckwargs = get_nested_community(community)
    return reverse(name_nested+"member-list", kwargs=ckwargs)


def rules_detail_url(community=None):
    community, ckwargs = get_nested_community(community)
    return reverse(name_nested+"rules-detail", kwargs=ckwargs)


class CommunityViewCaller(BaseCaller):
    def create__post(self, access_token,
                     type=COMM_TYPES.GROUP, name="my-gp",
                     allowed_status=status.HTTP_201_CREATED,
                     **body_kwargs):
        """Calls community-list view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            COMM_LIST_URL,
            data=(body_kwargs | {'type': type, 'name': name}),
            ** self.get_auth_header(access_token)
        )

    def retrieve__get(self, access_token, pk=None, creator=None,
                      allowed_status=status.HTTP_200_OK):
        """Calls community-detail view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            comm_detail_url(pk, creator),
            ** self.get_auth_header(access_token)
        )

    def pupdate__patch(self, access_token,
                       pk=None, creator=None, name="my-gp2",
                       allowed_status=status.HTTP_200_OK,
                       **body_kwargs):
        """Calls community-detail view with PATCH method"""
        return self.assert_status_code(
            allowed_status, self.client.patch,
            comm_detail_url(pk, creator),
            data=(body_kwargs | {'name': name}),
            ** self.get_auth_header(access_token)
        )

    def destroy__delete(self, access_token, pk=None, creator=None,
                        allowed_status=status.HTTP_204_NO_CONTENT):
        """Calls community-detail view with DELETE method"""
        return self.assert_status_code(
            allowed_status, self.client.delete,
            comm_detail_url(pk, creator),
            ** self.get_auth_header(access_token)
        )

    def create__link(self, access_token,
                     community: CommunityChat = None,
                     allowed_status=status.HTTP_201_CREATED):
        """Calls invite-link-list view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            invite_list_url(community),
            ** self.get_auth_header(access_token)
        )

    def list__link(self, access_token,
                   community: CommunityChat = None,
                   allowed_status=status.HTTP_200_OK):
        """Calls invite-link-list view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            invite_list_url(community),
            ** self.get_auth_header(access_token)
        )

    def destroy__link(self, access_token, pk=None,
                      community: CommunityChat = None,
                      allowed_status=status.HTTP_204_NO_CONTENT):
        """Calls invite-link-detail view with DELETE method"""

        return self.assert_status_code(
            allowed_status, self.client.delete,
            invite_detail_url(pk, community),
            ** self.get_auth_header(access_token)
        )

    def create__member(self, access_token,
                       community: CommunityChat = None,
                       allowed_status=status.HTTP_201_CREATED):
        """Calls member-list view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            member_list_url(community),
            ** self.get_auth_header(access_token)
        )

    def list__member(self, access_token,
                     community: CommunityChat = None,
                     allowed_status=status.HTTP_200_OK):
        """Calls member-list view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            member_list_url(community),
            ** self.get_auth_header(access_token)
        )

    def destroy__member(self, access_token, pk=None,
                        community: CommunityChat = None,
                        allowed_status=status.HTTP_204_NO_CONTENT):
        """Calls member-detail view with DELETE method"""
        return self.assert_status_code(
            allowed_status, self.client.delete,
            member_detail_url(pk, community),
            ** self.get_auth_header(access_token)
        )

    def pupdate__member(self, access_token, pk=None,
                        community: CommunityChat = None,
                        rank=Member.RankChoices.RESTRICTED,
                        allowed_status=status.HTTP_200_OK):
        """Calls member-detail view with PATCH method"""
        return self.assert_status_code(
            allowed_status, self.client.patch,
            member_detail_url(pk, community),
            data={'rank': rank},
            ** self.get_auth_header(access_token)
        )

    def ban__member(self, access_token, pk=None,
                    community: CommunityChat = None,
                    allowed_status=status.HTTP_200_OK):
        """Calls member-ban view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            member_ban_url(pk, community),
            ** self.get_auth_header(access_token)
        )

    def get__rules(self, access_token,
                   community: CommunityChat = None,
                   allowed_status=status.HTTP_200_OK):
        """Calls rules-detail view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            rules_detail_url(community),
            ** self.get_auth_header(access_token)
        )

    def pupdate__rules(self, access_token,
                       community: CommunityChat = None,
                       can_send_message=False,
                       allowed_status=status.HTTP_200_OK,
                       **body_kwargs):
        """Calls rules-detail view with PATCH method"""
        return self.assert_status_code(
            allowed_status, self.client.patch,
            rules_detail_url(community),
            data=body_kwargs | {
                'can_send_message': can_send_message},
            ** self.get_auth_header(access_token)
        )
