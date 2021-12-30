from django.test.testcases import TransactionTestCase

from .mixins import TokenTest
from .utils import create_device
from user.models import Device


class DeviceTest(TokenTest, TransactionTestCase):
    model = Device

    def create_instance(self):
        return create_device()
