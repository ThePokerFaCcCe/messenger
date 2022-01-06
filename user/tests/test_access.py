from django.test.testcases import TransactionTestCase
from rest_framework.test import APITransactionTestCase
from rest_framework import status

from user.models import Access
from .mixins import TokenTest
from .utils import (create_access, create_device,
                    AccessViewCaller)


class AccessModelTest(TokenTest, TransactionTestCase):
    model = Access

    def create_instance(self):
        return create_access()


class DeviceViewTest(APITransactionTestCase):
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
            token='Im#Bad',
            allowed_status=status.HTTP_404_NOT_FOUND
        )

    def test_success__retrieve(self):
        token = create_access().encrypted_token
        self.assertNumQueries(1, self.caller.retrieve__get,
                              token=token)
