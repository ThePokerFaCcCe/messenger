from django.test.testcases import TransactionTestCase
from rest_framework.test import APITransactionTestCase
from rest_framework import status

from auth_app.models import Access
from core.tests.mixins import TokenTest
from .utils import create_access
from user.tests.utils import create_device
from .utils.callers import AccessViewCaller


class AccessModelTest(TokenTest, TransactionTestCase):
    model = Access

    def create_instance(self):
        return create_access()


class AccessViewTest(APITransactionTestCase):
    caller: AccessViewCaller

    def setUp(self):
        self.caller = AccessViewCaller(self.client)

    def test_bad_device_token__create(self):
        self.caller.create__post(
            device_token='Im#Bad',
            allowed_status=status.HTTP_404_NOT_FOUND
        )

    def test_use_device_token_twice__create(self):
        d_token = create_device().encrypted_token
        self.caller.create__post(device_token=d_token)
        self.caller.create__post(
            device_token=d_token,
            allowed_status=status.HTTP_404_NOT_FOUND
        )

    def test_success__create(self):
        self.caller.create__post()

    def test_bad_token__retrieve(self):
        self.caller.retrieve__get(
            create_access(activate_user=True).encrypted_token,
            token='Im#Bad',
            allowed_status=status.HTTP_404_NOT_FOUND
        )

    def test_success__retrieve(self):
        token = create_access(activate_user=True).encrypted_token
        self.caller.retrieve__get(token, token=token)
