from typing import Callable
from django.urls.base import reverse_lazy
from rest_framework import status
from rest_framework.test import APIClient

from user.urls import app_name
from .creators import generate_email

VERIFYCODE_CREATE_URL = reverse_lazy(f"{app_name}:verify-code-list")
VERIFYCODE_CHECK_URL = reverse_lazy(f"{app_name}:verify-code-check")


class BaseCaller:
    client: APIClient

    def __init__(self, client: APIClient):
        self.client = client

    def assert_status_code(self, allowed_status,
                           view_caller: Callable,
                           *view_caller_args,
                           **view_caller_kwargs):
        res = view_caller(*view_caller_args,
                          **view_caller_kwargs)

        res_status = res.status_code
        assert res_status == allowed_status, (
            f'{res_status} != {allowed_status}'
        )
        return res


class VerifyCodeViewCaller(BaseCaller):

    def create__post(self, email=None,
                     allowed_status=status.HTTP_201_CREATED):
        """Calls verify-code-list view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            VERIFYCODE_CREATE_URL,
            data={'email': email or generate_email()}
        )

    def check__post(self, email, code,
                    allowed_status=status.HTTP_200_OK):
        """Calls verify-code-check view with POST method"""
        return self.assert_status_code(
            allowed_status, self.client.post,
            VERIFYCODE_CHECK_URL,
            data={'email': email, 'code': code}
        )
