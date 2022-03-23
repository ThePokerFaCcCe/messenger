from django.urls.base import reverse, reverse_lazy
from rest_framework import status

from user.models import Device
from user.urls import app_name
from core.tests.utils import BaseCaller
from auth_app.tests.utils import create_verifycode
from ..creators import create_device

DEVICE_LIST_URL = reverse_lazy(f"{app_name}:device-list")


def device_detail_url(token):
    return reverse(f"{app_name}:device-detail", kwargs={'token': token})


class DeviceViewCaller(BaseCaller):
    def create__post(self, verifycode_token=None,
                     device_type=Device.TypeChoices.WINDOWS,
                     device_model="10 Pro",
                     allowed_status=status.HTTP_201_CREATED):
        """Calls device-list view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            DEVICE_LIST_URL,
            data={
                'type': device_type, 'model': device_model,
                'verifycode_token': verifycode_token
                or create_verifycode(active_token=True).encrypted_token
            }
        )

    def retrieve__get(self, access_token, token=None,
                      allowed_status=status.HTTP_200_OK):
        """Calls device-detail view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            device_detail_url(token or create_device().encrypted_token),
            **self.get_auth_header(access_token)
        )
