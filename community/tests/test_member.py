from django.test.testcases import TestCase

from community.models import Member
from .utils import create_invite_link, create_member


class MemberModelTest(TestCase):
    def _assert_joined_by_contains(self, member: Member, text):
        found = member.joined_by.lower().find(text.lower())
        self.assertNotEqual(found, -1)

    def test_joined_by_link(self):
        member = create_member(
            _used_link=create_invite_link()
        )
        self._assert_joined_by_contains(member, 'link')

    def test_joined_by_guid(self):
        member = create_member(used_guid="iamyourguid")
        self._assert_joined_by_contains(member, 'guid')

    def test_joined_by_none(self):
        member = create_member()
        self.assertIsNone(member.joined_by)
