from django.test.testcases import TestCase

from user.tests.utils import create_active_user
from conversation.tests.utils import create_private_chat
from message.models import Message
from message.queryset import get_chat_messages
from .utils import create_deleted_msg, create_message
from core.tests.utils import assert_items_are_same_as_data


class MessageModelTest(TestCase):
    def setUp(self) -> None:
        self.user1 = create_active_user()
        self.user2 = create_active_user()
        self.pv = create_private_chat(self.user1, self.user2)

    def test_deleted_msgs_not_in_chat_queryset(self):
        msg1 = create_message(self.user1, self.pv)
        msg2 = create_message(self.user1, self.pv)
        msg3 = create_message(self.user2, self.pv)

        assert_items_are_same_as_data(
            items=[msg1.pk, msg2.pk, msg3.pk],
            data=get_chat_messages(self.pv.pk, self.user1.pk).values(),
            data_key='id'
        )

        msg2.soft_delete()

        assert_items_are_same_as_data(
            items=[msg1.pk, msg3.pk],
            data=get_chat_messages(self.pv.pk, self.user1.pk).values(),
            data_key='id'
        )

        assert_items_are_same_as_data(
            items=[msg1.pk, msg3.pk],
            data=get_chat_messages(self.pv.pk, self.user2.pk).values(),
            data_key='id'
        )

        create_deleted_msg(msg3, self.user1)

        assert_items_are_same_as_data(
            items=[msg1.pk],
            data=get_chat_messages(self.pv.pk, self.user1.pk).values(),
            data_key='id'
        )

        assert_items_are_same_as_data(
            items=[msg1.pk, msg3.pk],
            data=get_chat_messages(self.pv.pk, self.user2.pk).values(),
            data_key='id'
        )
