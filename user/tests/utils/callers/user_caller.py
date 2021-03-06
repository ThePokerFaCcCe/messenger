from django.urls.base import reverse, reverse_lazy
from rest_framework import status

from user.urls import app_name
from core.tests.utils import BaseCaller, create_image
from ..creators import create_user

# USER_LIST_URL = reverse_lazy(f"{app_name}:user-list")
USER_ME_DETAIL_URL = reverse_lazy(
    f"{app_name}:user-me-detail")
USER_ME_ALIVE_URL = reverse_lazy(
    f"{app_name}:user-me-send-alive")
USER_ME_PROFILE_URL = reverse_lazy(
    f"{app_name}:user-me-profile-image")


def user_detail_url(pk):
    return reverse(f"{app_name}:user-detail",
                   kwargs={'pk': pk})


def user_last_seen_url(pk):
    return reverse(f"{app_name}:user-last-seen",
                   kwargs={'pk': pk})


def user_profile_image_url(pk):
    return reverse(f"{app_name}:user-profile-image",
                   kwargs={'pk': pk})


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

    def last_seen__get(self, access_token, pk=None,
                       allowed_status=status.HTTP_200_OK
                       ):
        """Calls user-last-seen view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            user_last_seen_url(pk or create_user().pk),
            **self.get_auth_header(access_token)
        )

    def profile_image__get(self, access_token, pk=None,
                           allowed_status=status.HTTP_200_OK
                           ):
        """Calls user-profile-image view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            user_profile_image_url(pk or create_user().pk),
            **self.get_auth_header(access_token)
        )

    def profile_image__post(self, access_token, pk=None, image=None,
                            allowed_status=status.HTTP_200_OK
                            ):
        """Calls user-profile-image view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            user_profile_image_url(pk or create_user().pk),
            data={'profile_image': image or create_image()},
            format='multipart',
            **self.get_auth_header(access_token)
        )

    def profile_image__delete(self, access_token, pk=None,
                              allowed_status=status.HTTP_204_NO_CONTENT
                              ):
        """Calls user-profile-image view with DELETE method"""
        return self.assert_status_code(
            allowed_status, self.client.delete,
            user_profile_image_url(pk or create_user().pk),
            **self.get_auth_header(access_token)
        )

    def me__get(self, access_token,
                allowed_status=status.HTTP_200_OK):
        """Calls user-me view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            USER_ME_DETAIL_URL,
            **self.get_auth_header(access_token)
        )

    def me__patch(self, access_token,
                  allowed_status=status.HTTP_200_OK,
                  **update_kwargs):
        """Calls user-me view with PATCH method"""
        return self.assert_status_code(
            allowed_status, self.client.patch,
            USER_ME_DETAIL_URL,
            data=update_kwargs,
            **self.get_auth_header(access_token)
        )

    def me__send_alive__post(self, access_token,
                             allowed_status=status.HTTP_200_OK):
        """Calls user-send-alive view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            USER_ME_ALIVE_URL,
            **self.get_auth_header(access_token)
        )

    def me__profile_image__get(self, access_token,
                               allowed_status=status.HTTP_200_OK
                               ):
        """Calls user-me-profile-image view with GET method"""
        return self.assert_status_code(
            allowed_status, self.client.get,
            USER_ME_PROFILE_URL,
            **self.get_auth_header(access_token)
        )

    def me__profile_image__post(self, access_token, image=None,
                                allowed_status=status.HTTP_200_OK
                                ):
        """Calls user-me-profile-image view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            USER_ME_PROFILE_URL,
            data={'profile_image': image or create_image()},
            format='multipart',
            **self.get_auth_header(access_token)
        )

    def me__profile_image__delete(self, access_token,
                                  allowed_status=status.HTTP_204_NO_CONTENT
                                  ):
        """Calls user-me-profile-image view with DELETE method"""
        return self.assert_status_code(
            allowed_status, self.client.delete,
            USER_ME_PROFILE_URL,
            **self.get_auth_header(access_token)
        )
