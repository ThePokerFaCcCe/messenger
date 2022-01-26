from django.test.testcases import TestCase

from conversation.models import Conversation
from user.tests.utils import create_active_user
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
