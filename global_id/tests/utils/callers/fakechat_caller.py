from django.urls.base import reverse
from rest_framework import status

from global_id.tests.urls import app_name
from core.tests.utils import BaseCaller
from ..creators import create_fake_chat, generate_guid_string


def fakechat_guid_url(pk=None):
    return reverse(f"{app_name}:fake-chat-guid",
                   kwargs={"pk": pk or create_fake_chat().pk})


class FakeChatViewCaller(BaseCaller):
    def retrieve__guid(self, pk=None,
                       allowed_status=status.HTTP_200_OK):
        """Calls fake-chat-guid with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            fakechat_guid_url(pk)
        )

    def post__guid(self, pk=None, new_guid=None,
                   allowed_status=status.HTTP_200_OK):
        """Calls fake-chat-guid with POST method"""

        return self.assert_status_code(
            allowed_status, self.client.post,
            fakechat_guid_url(pk),
            data={'guid': new_guid or generate_guid_string()}
        )

    def delete__guid(self, pk=None,
                     allowed_status=status.HTTP_204_NO_CONTENT):
        """Calls fake-chat-guid with DELETE method"""
        return self.assert_status_code(
            allowed_status, self.client.delete,
            fakechat_guid_url(pk)
        )
