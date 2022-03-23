from django.urls.base import reverse, reverse_lazy
from rest_framework import status

from auth_app.urls import app_name
from core.tests.utils import BaseCaller
from user.tests.utils import create_device
from ..creators import create_access

ACCESS_LIST_URL = reverse_lazy(f"{app_name}:access-list")


def access_detail_url(token):
    return reverse(f"{app_name}:access-detail", kwargs={'token': token})


class AccessViewCaller(BaseCaller):
    def create__post(self, device_token=None,
                     allowed_status=status.HTTP_201_CREATED):
        """Calls access-list view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            ACCESS_LIST_URL,
            data={
                'device_token': device_token
                or create_device().encrypted_token
            }
        )

    def retrieve__get(self, access_token, token=None,
                      allowed_status=status.HTTP_200_OK):
        """Calls access-detail view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            access_detail_url(token or create_access().encrypted_token),
            **self.get_auth_header(access_token)
        )
