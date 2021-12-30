from django.test.testcases import TransactionTestCase

from .mixins import TokenTest
from .utils import create_access
from user.models import Access


class DeviceTest(TokenTest, TransactionTestCase):
    model = Access

    def create_instance(self):
        return create_access()
