import time
from datetime import timedelta
from unittest.mock import patch
from django.conf import settings
from django.test.testcases import TransactionTestCase

from user.models import VerifyCode
from .utils import create_verifycode
from .mixins import TokenTest


class VerifyCodeTest(TokenTest, TransactionTestCase):
    model = VerifyCode

    def create_instance(self):
        return create_verifycode()

    def test_not_expired_by_default(self):
        code = create_verifycode()
        self.assertEqual(code.expires_at, code.created_at + code.expire_after)
        self.assertEqual(code.is_expired, False)
        self.assertIn(code, VerifyCode.objects.filter_unexpired())
        self.assertNotIn(code, VerifyCode.objects.filter_expired())

    def test_expire_by_date(self):
        with patch.object(VerifyCode, 'expire_after',
                          new=timedelta(seconds=1)):
            code = create_verifycode()
            time.sleep(1.5)

            self.assertEqual(code.is_expired, True)
            self.assertIn(code, VerifyCode.objects.filter_expired())
            self.assertNotIn(code, VerifyCode.objects.filter_unexpired())

    def test_expire_by_tries(self):
        with patch.object(VerifyCode, 'expire_after',
                          new=timedelta(hours=2)):
            code = create_verifycode()
            for i in range(VerifyCode.max_tries):
                code.increase_tries()
            code.save()

            self.assertEqual(code.is_expired, True)
            self.assertIn(code, VerifyCode.objects.filter_expired())
            self.assertNotIn(code, VerifyCode.objects.filter_unexpired())

    def test_expire_by_is_used(self):
        with patch.object(VerifyCode, 'expire_after',
                          new=timedelta(hours=2)):
            code = create_verifycode()
            code.is_used = True
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

    def test_token_not_added_by_default(self):
        code = create_verifycode()
        self.assertIsNone(code.encrypted_token)

    def test_token_added_after_is_used_true(self):
        code = create_verifycode()
        code.is_used = True
        code.save()

        self.assertIsNotNone(code.encrypted_token)
