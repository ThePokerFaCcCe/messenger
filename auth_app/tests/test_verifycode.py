from django.conf import settings
from django.core import mail
from django.core.handlers.wsgi import WSGIRequest
from django.test.testcases import TransactionTestCase
from rest_framework import status
from rest_framework.test import APITransactionTestCase
from datetime import timedelta
from unittest.mock import patch
import time
import re

from auth_app.models import VerifyCode
from .utils import create_verifycode
from .utils.callers import VerifyCodeViewCaller
from core.utils import generate_email
from core.tests.mixins import TokenTest


class VerifyCodeModelTest(TokenTest, TransactionTestCase):
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

        code._dec_code = 0
        with patch.object(settings, 'VERIFYCODE_KEY', new="Different key"):
            self.assertIsNone(code.code)

    def test_token_not_added_by_default(self):
        code = create_verifycode()
        self.assertIsNone(code.encrypted_token)

    def test_token_added_after_is_used_true(self):
        code = create_verifycode()
        code.is_used = True
        code.save()

        self.assertIsNotNone(code.encrypted_token)


class VerifyCodeViewTest(APITransactionTestCase):
    caller: VerifyCodeViewCaller

    def setUp(self):
        self.caller = VerifyCodeViewCaller(self.client)

    def find_code(self, text):
        """Find code from entered text with regex"""
        code = re.search(VerifyCode.find_code_regex, text).group()
        self.assertIsNotNone(code, msg='Code not found in text')

        self.assertIsNotNone(
            re.search(VerifyCode.validation_regex, code),
            msg="The found code doesn't match with validation_regex")

        return code

    def find_code_from_mails(self):
        self.assertGreater(len(mail.outbox), 0,
                           msg='no mail saved in outbox')
        self.assertEqual(len(mail.outbox), 1,
                         msg='more than one mail saved in outbox')

        message = mail.outbox[0].body
        self.assertIsNotNone(message, msg='mail message is empty')

        return self.find_code(message)

    def test_bad_email__create(self):
        self.caller.create__post('imnotvalid',
                                 status.HTTP_400_BAD_REQUEST)

    def test_active_code_exists__create(self):
        email = generate_email()
        self.caller.create__post(email)
        self.caller.create__post(email,
                                 status.HTTP_400_BAD_REQUEST)

    def test_can_get_new_code_after_expire__create(self):
        email = generate_email()
        with patch.object(VerifyCode, 'expire_after',
                          new=timedelta(seconds=1)):
            self.caller.create__post(email)

            time.sleep(1.5)

            self.caller.create__post(email)

    def test_email_sent__create(self):
        email = generate_email()
        mail.outbox = []

        self.caller.create__post(email)

        self.find_code_from_mails()

    def test_success__create(self):
        self.caller.create__post()

    def test_bad_code__check(self):
        email = generate_email()

        self.caller.create__post(email)
        self.caller.check__post(email, 'W@EW#$&OKB ,¥‘',
                                status.HTTP_400_BAD_REQUEST)

    def test_wrong_code__check(self):
        email = generate_email()
        mail.outbox = []

        self.caller.create__post(email)

        code = self.find_code_from_mails()
        diff_code = code
        while diff_code == code:
            diff_code = VerifyCode.generate_code()

        self.caller.check__post(email, diff_code,
                                status.HTTP_404_NOT_FOUND)

    def test_wrong_email__check(self):
        self.caller.check__post(generate_email(),
                                VerifyCode.generate_code(),
                                status.HTTP_404_NOT_FOUND)

    def create_and_check_code(self) -> tuple[str, str, WSGIRequest]:
        """Create a code for email and check created code,
        returns (email, code, verify-code-check result)"""
        email = generate_email()
        mail.outbox = []

        self.caller.create__post(email)
        code = self.find_code_from_mails()
        res = self.caller.check__post(email, code)

        return (email, code, res)

    def test_success__check(self):
        self.create_and_check_code()

    def test_used_code_expires(self):
        email, code, res = self.create_and_check_code()
        self.caller.check__post(email, code,
                                status.HTTP_404_NOT_FOUND)

    def test_success_token_exists__check(self):
        email, code, res = self.create_and_check_code()
        self.assertIn('token', res.data.keys())

        token = res.data['token']
        self.assertIsNotNone(
            VerifyCode.objects.find_token(token))

    def test_success_user_will_active__create(self):
        verifycode = create_verifycode()
        user = verifycode.user

        self.assertFalse(user.is_active,
                         "User is already active")
        self.caller.check__post(user.email, verifycode.code)

        user.refresh_from_db()
        self.assertTrue(user.is_active,
                        "User isn't active")
