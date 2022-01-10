from django.test.testcases import TransactionTestCase
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from user.models import Device
from core.tests.mixins import TokenTest
from auth_app.tests.utils import create_verifycode
from .utils.callers import DeviceViewCaller
from .utils.creators import create_device


class DeviceModelTest(TokenTest, TransactionTestCase):
    model = Device

    def create_instance(self):
        return create_device()


class DeviceViewTest(APITransactionTestCase):
    caller: DeviceViewCaller

    def setUp(self):
        self.caller = DeviceViewCaller(self.client)

    def test_bad_verifycode_token__create(self):
        self.caller.create__post(
            verifycode_token='Im#Bad',
            allowed_status=status.HTTP_404_NOT_FOUND
        )

    def test_bad_device_type__create(self):
        self.caller.create__post(
            device_type='Im#Bad',
            allowed_status=status.HTTP_400_BAD_REQUEST
        )

    def test_use_verifycode_token_twice__create(self):
        v_token = create_verifycode(active_token=True).encrypted_token
        self.caller.create__post(verifycode_token=v_token)
        self.caller.create__post(
            verifycode_token=v_token,
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
        self.caller.retrieve__get()
