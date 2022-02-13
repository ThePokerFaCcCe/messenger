from django.test.testcases import TransactionTestCase
from rest_framework import test, status
from django.contrib.contenttypes.models import ContentType

from core.utils import get_list_of_dict_values
from core.tests.utils import assert_items_are_same_as_data
from community.models import CommunityChat, Member
from auth_app.tests.utils import create_access
from .utils import create_community_chat, create_member, create_invite_link
from .utils.callers import CommunityViewCaller

RANKS = Member.RankChoices


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


class CommunityViewTest(test.APITransactionTestCase):
    caller: CommunityViewCaller

    def __create_member_access(self, rank, community=None):
        community = community or self.comm
        access = create_access(activate_user=True)
        member = create_member(
            community, access.user, rank
        )
        access_token = access.encrypted_token
        return access_token, member

    def setUp(self) -> None:
        self.caller = CommunityViewCaller(self.client)
        access = create_access(activate_user=True)
        self.user = access.user
        self.access = access.encrypted_token
        self.comm = create_community_chat(creator=self.user)

        self.normal_access, self.normal_member\
            = self.__create_member_access(RANKS.NORMAL)

        self.admin_access, self.admin_member\
            = self.__create_member_access(RANKS.ADMIN)

    def test_create_group_community(self):
        self.caller.create__post(self.access)

    def test_created_community_owner_is_self(self):
        comm_pk = self.caller.create__post(self.access).data['id']
        comm = CommunityChat.objects\
            .select_related('creator').get(pk=comm_pk)
        self.assertEqual(self.user, comm.creator)

    def test_update_community_by_owner(self):
        self.caller.pupdate__patch(self.access, self.comm.pk)

    def test_update_community_by_admin(self):
        self.caller.pupdate__patch(self.admin_access, self.comm.pk)

    def test_update_community_fails_by_member(self):
        self.caller.pupdate__patch(
            self.normal_access, self.comm.pk,
            allowed_status=status.HTTP_403_FORBIDDEN)

    def test_create_invite_link(self):
        self.caller.create__link(self.access, self.comm)

    def test_create_invite_link_fails_by_member(self):
        self.caller.create__link(
            self.normal_access, self.comm,
            allowed_status=status.HTTP_403_FORBIDDEN)

    def test_soft_deleted_invite_link(self):
        link = create_invite_link(self.comm)
        self.caller.destroy__link(self.access, pk=link.pk, community=self.comm)
        link.refresh_from_db()

        self.assertIsNotNone(
            link.pk, msg="invite link doesn't use soft delete")

        self.assertTrue(
            link.is_deleted, msg='link soft delete has bugs'
        )

    def test_list_link_works_fine(self):
        self.comm.invite_links.all().delete()
        links = [create_invite_link(self.comm).pk,
                 create_invite_link(self.comm).pk]
        different_link = create_invite_link().pk
        data = self.caller.list__link(self.access, self.comm).data
        assert_items_are_same_as_data(items=links, data=data)

    def test_list_members_success_by_member(self):
        self.caller.list__member(self.normal_access, self.comm)

    def test_list_members_works_fine(self):
        comm = create_community_chat(creator=self.user)
        members = [
            create_member(comm).user.pk,
            create_member(comm).user.pk,
            self.user.pk
        ]
        different_member = create_member()
        data = self.caller.list__member(self.access, comm).data
        data = get_list_of_dict_values(data, 'user')
        assert_items_are_same_as_data(items=members, data=data)

    def test_restrict_member(self):
        self.caller.pupdate__member(
            self.access, self.normal_member.user.pk,
            self.comm, rank=RANKS.ADMIN)

    def test_self_admin_ban_itself_fail(self):
        self.caller.ban__member(
            self.access, self.user.pk, self.comm,
            allowed_status=status.HTTP_403_FORBIDDEN)

    def test_self_owner_unrank_itself_fail(self):
        self.caller.pupdate__member(
            self.access, self.user.pk, self.comm,
            rank=RANKS.NORMAL, allowed_status=status.HTTP_403_FORBIDDEN)

    def test_make_member_owner(self):
        self.caller.pupdate__member(
            self.access, self.normal_member.user.pk, self.comm,
            rank=RANKS.OWNER, allowed_status=status.HTTP_400_BAD_REQUEST)

    def test_normal_member_make_itself_admin_fail(self):
        self.caller.pupdate__member(
            self.normal_access, self.normal_member.user.pk, self.comm,
            rank=RANKS.ADMIN, allowed_status=status.HTTP_403_FORBIDDEN)

    def test_ban_member(self):
        self.caller.ban__member(
            self.access, self.normal_member.user.pk, self.comm
        )

    def test_ban_owner_by_admin_fail(self):
        self.caller.ban__member(
            self.admin_access, self.user.pk, self.comm,
            allowed_status=status.HTTP_403_FORBIDDEN
        )

    def test_fail_ban_by_normal_member(self):
        self.caller.ban__member(
            self.normal_access, self.admin_member.user.pk, self.comm,
            allowed_status=status.HTTP_403_FORBIDDEN)

    def test_edit_rules(self):
        self.caller.pupdate__rules(self.access, self.comm,)

    def test_edit_rules_fail_by_normal_member(self):
        self.caller.pupdate__rules(
            self.normal_access, self.comm,
            allowed_status=status.HTTP_403_FORBIDDEN)
