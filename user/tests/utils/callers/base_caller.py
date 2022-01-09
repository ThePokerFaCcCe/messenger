from typing import Callable
from rest_framework.test import APIClient


class BaseCaller:
    client: APIClient

    def __init__(self, client: APIClient):
        self.client = client

    def get_auth_header(self, access_token) -> dict:
        """Return HTTP_AUTHORIZATION header"""
        return {"HTTP_AUTHORIZATION": f'Token {access_token}'}

    def assert_status_code(self, allowed_status,
                           view_caller: Callable,
                           *view_caller_args,
                           **view_caller_kwargs):
        res = view_caller(*view_caller_args,
                          **view_caller_kwargs)

        res_status = res.status_code
        assert res_status == allowed_status, (
            f'{res_status} != {allowed_status}\n{res.data}'
        )
        return res
