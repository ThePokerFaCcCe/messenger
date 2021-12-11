from datetime import timedelta
from django.test.testcases import TransactionTestCase
from django.test import TestCase
from django.core.exceptions import ValidationError
from uuid import uuid4
import time


from user.models import User


def create_user(email=None, **kwargs) -> User:
    email = f'{uuid4()}@gmail.com' if not email else email

    return User.objects.create_user(email, **kwargs)


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
        user.offline_after_sec = timedelta(seconds=2)
        self.assertEqual(user.is_online, True)
        time.sleep(3)
        self.assertEqual(user.is_online, False)
