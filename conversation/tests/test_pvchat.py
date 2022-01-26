from django.test.testcases import TestCase

from conversation.models import PrivateChat
from user.tests.utils import create_active_user
from .utils import create_private_chat


class PrivateChatModelTest(TestCase):
    def setUp(self) -> None:
        self.user = create_active_user()
        self.user2 = create_active_user()

    def test_create_pvchat(self):
        pv = create_private_chat(self.user, self.user2)

        found_pv = PrivateChat.objects.filter(
            users=[self.user, self.user2]
        )

        self.assertTrue(
            found_pv.exists(), "created pv not found in db"
        )
        self.assertEqual(len(found_pv), 1,
                         "More than 1 pvchat found in db"
                         )
        self.assertIn(pv, found_pv)

    def test_another_pvchat_not_in_qs(self):
        user3 = create_active_user()
        pv1 = create_private_chat(self.user, self.user2)
        pv2 = create_private_chat(self.user, user3)

        found_pv1 = PrivateChat.objects.filter(
            users=[self.user, self.user2]
        )

        self.assertIn(pv1, found_pv1)
        self.assertNotIn(pv2, found_pv1)

        found_pv2 = PrivateChat.objects.filter(
            users=[self.user, user3]
        )

        self.assertIn(pv2, found_pv2)
        self.assertNotIn(pv1, found_pv2)

    def test_another_user_not_in_qs(self):
        user3 = create_active_user()
        create_private_chat(self.user, self.user2)

        found_pv = PrivateChat.objects.filter(
            users=[self.user, user3]
        )
        self.assertFalse(
            found_pv.exists(),
            "unexpected pvchat found"
        )
