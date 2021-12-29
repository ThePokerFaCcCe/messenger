from django.test.testcases import TransactionTestCase

from .utils import create_device
from user.models import Device


class DeviceTest(TransactionTestCase):

    def test_token_hashed(self):
        device = create_device()
        self.assertNotEqual(device._token_length, len(device.token))

    def test_unhashed_token(self):
        device = create_device()
        self.assertIsNotNone(device.unhashed_token)
        self.assertNotEqual(device.unhashed_token, device.token)

    def test_find_token(self):
        device = create_device()
        self.assertEqual(device,
                         Device.objects.find_token(device.unhashed_token))

        device_2 = create_device()
        self.assertNotEqual(device_2,
                            Device.objects.find_token(device.unhashed_token))
