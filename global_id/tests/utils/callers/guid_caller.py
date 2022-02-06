from django.urls.base import reverse
from rest_framework import status

from global_id.urls import app_name
from core.tests.utils import BaseCaller
from ..creators import create_guid


def guid_detail_url(guid=None):
    return reverse(f"{app_name}:guid-detail",
                   kwargs={'guid': guid or create_guid().guid})


class GUIDViewCaller(BaseCaller):
    def retrieve__get(self, access_token, guid: str = None,
                      allowed_status=status.HTTP_200_OK):
        """Calls guid-detail view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            guid_detail_url(guid),
            **self.get_auth_header(access_token)
        )
