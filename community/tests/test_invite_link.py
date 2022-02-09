from django.test.testcases import TestCase
from django.core.exceptions import ValidationError

from .utils import create_invite_link


class InviteLinkModelTest(TestCase):
    def setUp(self) -> None:
        self.link = create_invite_link()

    def test_is_deleted_is_none(self):
        self.assertIsNone(self.link.deleted_at)

    def test_is_deleted_sets_once(self):
        self.link.is_deleted = True
        self.link.save()

        delete_date = self.link.deleted_at
        self.assertIsNotNone(
            delete_date, 'delete date not set')

        self.link.save()
        self.assertEqual(
            self.link.deleted_at, delete_date
        )
