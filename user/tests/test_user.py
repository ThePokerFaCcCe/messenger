import time
from django.test.testcases import TransactionTestCase
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITransactionTestCase
from datetime import timedelta

from auth_app.tests.utils import create_access
from .utils.creators import create_user
from .utils.callers import UserViewCaller


class UserModelTest(TransactionTestCase):
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


class DeviceViewTest(APITransactionTestCase):
    caller: UserViewCaller

    def setUp(self):
        self.caller = UserViewCaller(self.client)
        self.user = create_user(is_active=True)
        self.access = create_access(user=self.user
                                    ).encrypted_token
        self.staff_access = create_access(
            user=create_user(is_active=True, is_staff=True)
        ).encrypted_token

    def test_access_without_token(self):
        user = create_user()
        self.caller.retrieve__get(None, user.pk,
                                  status.HTTP_401_UNAUTHORIZED)

    def test_access_with_token(self):
        user = create_user()
        self.caller.retrieve__get(self.access, user.pk)

    def test_update_self__p_update(self):
        self.caller.p_update__patch(
            self.access, self.user.pk,
            first_name="Iam new name"
        )

    def test_user_update_others__p_update(self):
        user = create_user()
        self.caller.p_update__patch(
            self.access, user.pk,
            first_name="Iam new name",
            allowed_status=status.HTTP_403_FORBIDDEN
        )

    def test_staff_update_others__p_update(self):
        user = create_user()
        self.caller.p_update__patch(
            self.staff_access, user.pk,
            first_name="Iam new name",
        )

    def test_staff_update_others_set_scam__p_update(self):
        user = create_user()
        self.caller.p_update__patch(
            self.staff_access, user.pk,
            is_scam=True,
        )
        user.refresh_from_db()
        self.assertTrue(user.is_scam,
                        "Staff cant set scam to user")

    def test_get_user__me(self):
        self.caller.me__get(self.access)

    def test_update_self__me(self):
        self.caller.me__patch(
            self.access, first_name="Iam new name"
        )

    def test_update_self_add_is_staff__me(self):
        self.caller.me__patch(
            self.access, is_staff=True
        )
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff,
                         'User can set staff perm to itself')
