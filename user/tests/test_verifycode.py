import time
from datetime import timedelta
from django.conf import settings
from django.test.testcases import TransactionTestCase

from user.models import VerifyCode
from .utils import create_verifycode


class VerifyCodeTest(TransactionTestCase):
    """
    test is_expired
    """

    def test_expire(self):
        code = create_verifycode()
        self.assertEqual(code.expires_at, code.created_at + code.expire_after)
        self.assertEqual(code.is_expired, False)
        self.assertIn(code, VerifyCode.objects.filter_unexpired())
        self.assertNotIn(code, VerifyCode.objects.filter_expired())

        VerifyCode.expire_after = timedelta(seconds=1)
        time.sleep(1.5)

        self.assertEqual(code.is_expired, True)
        self.assertIn(code, VerifyCode.objects.filter_expired())
        self.assertNotIn(code, VerifyCode.objects.filter_unexpired())

        VerifyCode.expire_after = timedelta(hours=2)

        code = create_verifycode()
        for i in range(VerifyCode.max_tries):
            code.increase_tries()
        code.save()

        self.assertEqual(code.is_expired, True)
        self.assertIn(code, VerifyCode.objects.filter_expired())
        self.assertNotIn(code, VerifyCode.objects.filter_unexpired())

    def test_encryption(self):
        code = create_verifycode()

        self.assertTrue(code.check_code(code.code))
        self.assertNotEqual(code.code, code._code)

        settings.VERIFYCODE_KEY = "Different key"
        code._dec_code = 0
        self.assertIsNone(code.code)
