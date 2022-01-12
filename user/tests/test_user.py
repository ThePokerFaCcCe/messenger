from django.test.testcases import TransactionTestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITransactionTestCase
from datetime import timedelta
from unittest.mock import patch
import time

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
        with patch.object(user, 'offline_after',
                          new=timedelta(seconds=1)):
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

    def test_online__last_seen__get(self):
        user = create_user()
        user.set_online()

        res = self.caller.last_seen__get(self.access, pk=user.pk)
        self.assertTrue(res.data['is_online'])

        self.assertEqual(
            user.next_offline,
            res.data['next_offline']
        )

    def test_offline__last_seen__get(self):
        user = create_user()
        user.last_seen = timezone.now()-timedelta(weeks=999)
        user.save()

        res = self.caller.last_seen__get(self.access, pk=user.pk)
        self.assertFalse(res.data['is_online'])

        self.assertIsNone(res.data['next_offline'])

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

    def test_send_alive__me(self):
        old_last_seen = self.user.last_seen
        res = self.caller.me__send_alive__post(self.access)

        self.user.refresh_from_db()

        self.assertTrue(res.data['is_online'])

        self.assertEqual(
            self.user.next_offline,
            res.data['next_offline']
        )

        self.assertGreater(
            self.user.last_seen, old_last_seen
        )
