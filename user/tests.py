from datetime import timedelta
from django.conf import settings
from django.test.testcases import TransactionTestCase
from django.test import TestCase
from django.core.exceptions import ValidationError
from uuid import uuid4
import time

from user.models import User, VerifyCode


def generate_email(domain="gmail.com") -> str:
    """Create random email with uuid"""
    return f'{uuid4()}@{domain}'


def create_user(email=None, **kwargs) -> User:
    email = generate_email() if not email else email
    return User.objects.create_user(email, **kwargs)


def create_verifycode(user=None, **kwargs) -> VerifyCode:
    user = create_user() if not user else user
    code = VerifyCode.objects.create(user=user, **kwargs)
    code.refresh_from_db()
    return code


class UserTest(TransactionTestCase):
    # Reason of using TransactionTestCase:
    # https://stackoverflow.com/a/43981107/14034832

    def test_start_user_id(self):
        user = create_user()
        self.assertGreaterEqual(user.id, user.start_count_value)

    def test_valid_username(self):
        invalid_usernames = [
            '$Matin_Kh>',
            '_matinkh',
            '0matinkh',
            'matinkh_',
            'matin__kh',
            'matin_kh_n',
            'mat',
            'matin'*120,
        ]

        valid_usernames = [
            'matin13_81khaleghi',
            'matin1381kh',
        ]
        for un in invalid_usernames:
            create_user(username=un)
            self.assertRaises(ValidationError)

        for un in valid_usernames:
            create_user(username=un)

    def test_is_online(self):
        user = create_user()
        user.set_online()
        self.assertEqual(user.is_online, True)
        user.offline_after = timedelta(seconds=1)
        time.sleep(1.5)
        self.assertEqual(user.is_online, False)


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
