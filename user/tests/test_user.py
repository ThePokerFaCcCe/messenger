from django.test.testcases import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import timedelta
from unittest.mock import patch
import time

from auth_app.tests.utils import create_access
from .utils.creators import create_user
from .utils.callers import UserViewCaller


class UserModelTest(TestCase):
    def test_is_online(self):
        user = create_user()
        user.set_online()
        self.assertEqual(user.is_online, True)
        with patch.object(user, 'offline_after',
                          new=timedelta(seconds=1)):
            time.sleep(1.5)
            self.assertEqual(user.is_online, False)


class DeviceViewTest(APITestCase):
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
            user.next_offline.isoformat(),
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
            self.user.next_offline.isoformat(),
            res.data['next_offline']
        )

        self.assertGreater(
            self.user.last_seen, old_last_seen
        )

    def test_get_profile_image__me(self):
        self.caller.me__profile_image__get(
            self.access
        )

    def create_profile_image_tests(self, post_func,
                                   get_func, **func_kwargs):
        res_post = post_func(**func_kwargs)
        self.assertIsNotNone(res_post.data['profile_image'])
        self.assertIsNotNone(
            res_post.data['profile_image']['image'])
        self.assertIsNotNone(
            res_post.data['profile_image']['image']['url'])

        res_get = get_func(**func_kwargs)
        self.assertEqual(
            res_post.data['profile_image']['image']['url'],
            res_get.data['profile_image']['image']['url'],
        )

        self.assertEqual(
            res_post.data['profile_image']['thumbnail']['url'],
            res_get.data['profile_image']['thumbnail']['url'],
        )

    def delete_profile_image_tests(self, del_func,
                                   get_func, **func_kwargs):
        del_func(**func_kwargs)

        res_get = get_func(**func_kwargs)
        self.assertIsNone(res_get.data['profile_image'])

    def test_create_profile_image__me(self):
        self.user.delete_profile_image()

        self.create_profile_image_tests(
            self.caller.me__profile_image__post,
            self.caller.me__profile_image__get,
            access_token=self.access,
        )

    def test_update_profile_image__me(self):
        self.caller.me__profile_image__post(
            self.access
        )

        self.create_profile_image_tests(
            self.caller.me__profile_image__post,
            self.caller.me__profile_image__get,
            access_token=self.access
        )

    def test_delete_profile_image__me(self):
        self.delete_profile_image_tests(
            self.caller.me__profile_image__delete,
            self.caller.me__profile_image__get,
            access_token=self.access
        )

    def test_self_profile_image__create(self):
        self.user.delete_profile_image()

        self.create_profile_image_tests(
            self.caller.profile_image__post,
            self.caller.profile_image__get,
            access_token=self.access,
            pk=self.user.pk,
        )

    def test_self_profile_image__update(self):
        self.caller.me__profile_image__post(
            self.access
        )

        self.create_profile_image_tests(
            self.caller.profile_image__post,
            self.caller.profile_image__get,
            access_token=self.access,
            pk=self.user.pk,
        )

    def test_self_profile_image__delete(self):
        self.delete_profile_image_tests(
            self.caller.profile_image__delete,
            self.caller.profile_image__get,
            access_token=self.access,
            pk=self.user.pk,
        )

    def test_get_others_profile_image(self):
        self.caller.profile_image__get(
            self.access
        )

    def test_user_update_others_profile_image(self):
        self.caller.profile_image__post(
            self.access,
            allowed_status=status.HTTP_403_FORBIDDEN
        )

    def test_staff_update_others_profile_image(self):
        self.caller.profile_image__post(
            self.staff_access,
        )

    def test_user_delete_others_profile_image(self):
        self.caller.profile_image__delete(
            self.access,
            allowed_status=status.HTTP_403_FORBIDDEN
        )

    def test_staff_delete_others_profile_image(self):
        self.caller.profile_image__delete(
            self.staff_access,
        )
