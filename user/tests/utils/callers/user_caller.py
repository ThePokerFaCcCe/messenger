from django.urls.base import reverse, reverse_lazy
from rest_framework import status

from user.urls import app_name
from .base_caller import BaseCaller
from ..creators import create_access, create_user

# USER_LIST_URL = reverse_lazy(f"{app_name}:user-list")
USER_ME_URL = reverse_lazy(f"{app_name}:user-me")


def user_detail_url(pk):
    return reverse(f"{app_name}:user-detail", kwargs={'pk': pk})


class UserViewCaller(BaseCaller):
    def retrieve__get(self, access_token, pk=None,
                      allowed_status=status.HTTP_200_OK):
        """Calls user-detail view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            user_detail_url(pk or create_user().pk),
            **self.get_auth_header(access_token)
        )

    def p_update__patch(self, access_token, pk=None,
                        allowed_status=status.HTTP_200_OK,
                        **update_kwargs):
        """Calls user-detail view with PATCH method"""
        return self.assert_status_code(
            allowed_status, self.client.patch,
            user_detail_url(pk or create_user().pk),
            data=update_kwargs,
            **self.get_auth_header(access_token)
        )

    def me__get(self, access_token,
                allowed_status=status.HTTP_200_OK):
        """Calls user-me view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            USER_ME_URL,
            **self.get_auth_header(access_token)
        )

    def me__patch(self, access_token,
                  allowed_status=status.HTTP_200_OK,
                  **update_kwargs):
        """Calls user-me view with PATCH method"""
        return self.assert_status_code(
            allowed_status, self.client.patch,
            USER_ME_URL,
            data=update_kwargs,
            **self.get_auth_header(access_token)
        )
