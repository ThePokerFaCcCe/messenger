from django.urls.base import reverse, reverse_lazy
from rest_framework import status

from conversation.models import Conversation
from conversation.urls import app_name
from core.tests.utils import BaseCaller
from ..creators import create_conversation

CONV_LIST_URL = reverse_lazy(f"{app_name}:conversation-list")


def conv_detail_url(pk):
    return reverse(f"{app_name}:conversation-detail", kwargs={'pk': pk})


def conv_pin_url(pk):
    return reverse(f"{app_name}:conversation-pin", kwargs={'pk': pk})


def conv_unpin_url(pk):
    return reverse(f"{app_name}:conversation-unpin", kwargs={'pk': pk})


def conv_archive_url(pk):
    return reverse(f"{app_name}:conversation-archive", kwargs={'pk': pk})


def conv_unarchive_url(pk):
    return reverse(f"{app_name}:conversation-unarchive", kwargs={'pk': pk})


def conv_alias_url(pk):
    return reverse(f"{app_name}:conversation-alias", kwargs={'pk': pk})


class ConversationViewCaller(BaseCaller):
    def list__get(self, access_token, allowed_status=status.HTTP_200_OK):
        """Calls conversation-list view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            CONV_LIST_URL,
            **self.get_auth_header(access_token)
        )

    def retrieve__get(self, access_token, pk=None, user=None,
                      allowed_status=status.HTTP_200_OK):
        """Calls conversation-retrieve view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            conv_detail_url(pk if pk else
                            create_conversation(user=user).pk),
            **self.get_auth_header(access_token)
        )

    def pupdate__patch(self, access_token, pk=None, user=None,
                       allowed_status=status.HTTP_200_OK,
                       **update_kwargs):
        """Calls conversation-pupdate view with PATCH method"""
        return self.assert_status_code(
            allowed_status, self.client.patch,
            conv_detail_url(pk if pk else
                            create_conversation(user=user).pk),
            data=update_kwargs,
            **self.get_auth_header(access_token)
        )

    def destroy__delete(self, access_token, pk=None, user=None,
                        allowed_status=status.HTTP_204_NO_CONTENT):
        """Calls conversation-destroy view with DELETE method"""
        return self.assert_status_code(
            allowed_status, self.client.delete,
            conv_detail_url(pk if pk else
                            create_conversation(user=user).pk),
            **self.get_auth_header(access_token)
        )

    def pin__post(self, access_token, pk=None, user=None,
                  allowed_status=status.HTTP_200_OK):
        """Calls conversation-pin view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            conv_pin_url(pk if pk else
                         create_conversation(user=user).pk),
            **self.get_auth_header(access_token)
        )

    def unpin__post(self, access_token, pk=None, user=None,
                    allowed_status=status.HTTP_200_OK):
        """Calls conversation-unpin view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            conv_unpin_url(pk if pk else
                           create_conversation(user=user).pk),
            **self.get_auth_header(access_token)
        )

    def archive__post(self, access_token, pk=None, user=None,
                      allowed_status=status.HTTP_200_OK):
        """Calls conversation-archive view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            conv_archive_url(pk if pk else
                             create_conversation(user=user).pk),
            **self.get_auth_header(access_token)
        )

    def unarchive__post(self, access_token, pk=None, user=None,
                        allowed_status=status.HTTP_200_OK):
        """Calls conversation-unarchive view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            conv_unarchive_url(pk if pk else
                               create_conversation(user=user).pk),
            **self.get_auth_header(access_token)
        )

    def alias__post(self, access_token, pk=None, user=None,
                    alias="Alias!",
                    allowed_status=status.HTTP_200_OK):
        """Calls conversation-alias view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            conv_alias_url(pk if pk else
                           create_conversation(user=user).pk),
            data={"alias": alias},
            **self.get_auth_header(access_token)
        )
