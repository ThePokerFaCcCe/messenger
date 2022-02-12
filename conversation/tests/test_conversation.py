from django.test.testcases import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from conversation.models import Conversation
from conversation.tests.utils.callers import ConversationViewCaller
from core.tests.utils import assert_items_are_same_as_data
from core.utils import get_list_of_dict_values
from user.tests.utils import create_active_user
from auth_app.tests.utils import create_access
from .utils import create_conversation, create_private_chat


class ConversationModelTest(TestCase):
    def test_create_conversation(self):
        conv = create_conversation()
        create_conversation()

        found_conv = Conversation.objects.filter(
            chat_content_type=conv.chat_content_type,
            chat_id=conv.chat_id
        )

        self.assertIn(conv, found_conv)

    def test_pvchat_type_is_correct(self):
        pv = create_private_chat()
        conv = create_conversation(chat=pv)

        self.assertEqual(conv.type,
                         conv.TypeChoices.PRIVATE)


class ConversationViewTest(APITestCase):
    caller: ConversationViewCaller
    """
delete
"""

    def setUp(self):
        self.caller = ConversationViewCaller(self.client)
        self.user = create_active_user()
        self.access = create_access(user=self.user
                                    ).encrypted_token

    def test_list_all_convs(self):
        convs = [create_conversation(user=self.user).pk,
                 create_conversation(user=self.user).pk]

        res = self.caller.list__get(self.access)

        assert_items_are_same_as_data(items=convs, data=res.data)

    def test_list_not_show_others_conv(self):
        c1 = create_conversation(user=self.user).pk
        c2 = create_conversation().pk

        res = self.caller.list__get(self.access)
        pks = get_list_of_dict_values(res.data, 'id')

        self.assertIn(c1, pks)
        self.assertNotIn(c2, pks)

    def test_retrieve_self_conv(self):
        self.caller.retrieve__get(self.access, user=self.user)

    def test_retrieve_others_conv(self):
        c = create_conversation().pk

        self.caller.retrieve__get(
            self.access, pk=c,
            allowed_status=status.HTTP_404_NOT_FOUND)

    def test_update_self_conv(self):
        c = create_conversation(
            user=self.user, is_pinned=False, alias=None)
        alias = "My Guys"
        self.caller.pupdate__patch(
            self.access, pk=c.pk,
            is_pinned=True, alias=alias)
        c.refresh_from_db()
        self.assertTrue(
            all([c.is_pinned == True, c.alias == alias])
        )

    def test_pin_conv(self):
        c = create_conversation(user=self.user, is_pinned=False)
        self.caller.pin__post(self.access, c.pk)
        c.refresh_from_db()
        self.assertTrue(c.is_pinned)

    def test_pin_pinned_conv(self):
        c = create_conversation(user=self.user, is_pinned=True)
        self.caller.pin__post(
            self.access, c.pk,
            allowed_status=status.HTTP_400_BAD_REQUEST)

    def test_unpin_conv(self):
        c = create_conversation(user=self.user, is_pinned=True)
        self.caller.unpin__post(self.access, c.pk)
        c.refresh_from_db()
        self.assertFalse(c.is_pinned)

    def test_unpin_unpinned_conv(self):
        c = create_conversation(user=self.user, is_pinned=False)
        self.caller.unpin__post(
            self.access, c.pk,
            allowed_status=status.HTTP_400_BAD_REQUEST)

    def test_archive_conv(self):
        c = create_conversation(user=self.user, is_archived=False)
        self.caller.archive__post(self.access, c.pk)
        c.refresh_from_db()
        self.assertTrue(c.is_archived)

    def test_archive_pinned_conv(self):
        c = create_conversation(user=self.user, is_archived=True)
        self.caller.archive__post(
            self.access, c.pk,
            allowed_status=status.HTTP_400_BAD_REQUEST)

    def test_unarchive_conv(self):
        c = create_conversation(user=self.user, is_archived=True)
        self.caller.unarchive__post(self.access, c.pk)
        c.refresh_from_db()
        self.assertFalse(c.is_archived)

    def test_unarchive_unpinned_conv(self):
        c = create_conversation(user=self.user, is_archived=False)
        self.caller.unarchive__post(
            self.access, c.pk,
            allowed_status=status.HTTP_400_BAD_REQUEST)

    def test_set_alias_conv(self):
        c = create_conversation(user=self.user)
        alias = 'My Guys'
        self.caller.alias__post(self.access, pk=c.pk, alias=alias)
        c.refresh_from_db()
        self.assertEqual(c.alias, alias)

    def test_delete_conv(self):
        self.caller.destroy__delete(self.access, user=self.user)
