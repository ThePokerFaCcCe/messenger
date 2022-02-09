from django.test.testcases import TransactionTestCase
from django.contrib.contenttypes.models import ContentType

from .utils import create_community_chat


class CommunityModelTest(TransactionTestCase):

    def setUp(self) -> None:
        self.comm = create_community_chat()
        self.user = self.comm.creator

    def test_owner_member_creates(self):
        self.assertIsNotNone(
            self.user, msg='owner not created'
        )

        member = self.comm.members.filter(user=self.user)
        self.assertTrue(member.exists(),
                        msg='owner isnt in members')

    def test_owner_conv_creates(self):
        ctype = ContentType.objects.get_for_model(self.comm.__class__)
        conv = self.user.chats.filter(
            chat_content_type=ctype,
            chat_id=self.comm.pk
        )
        self.assertTrue(conv.exists(),
                        msg='owner conv not created')
