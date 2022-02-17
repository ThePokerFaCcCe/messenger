from django.test.testcases import TransactionTestCase
from rest_framework import test, status
from django.contrib.contenttypes.models import ContentType

from conversation.models import Conversation
from core.utils import get_list_of_dict_values
from core.tests.utils import assert_items_are_same_as_data
from community.models import CommunityChat, Member
from community.models.utils import generate_invite_link
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
        self.link = create_invite_link(self.comm)
        self.normal_access, self.normal_member\
            = self.__create_member_access(RANKS.NORMAL)
        self.admin_access, self.admin_member\
            = self.__create_member_access(RANKS.ADMIN)
        anonymous_access = create_access(activate_user=True)
        self.anonymous_access = anonymous_access.encrypted_token
        self.anonymous_user = anonymous_access.user

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

    def __join_anonymus_to_link(self, status=status.HTTP_204_NO_CONTENT):
        self.caller.post__join(self.anonymous_access, invite_link=self.link.link,
                               allowed_status=status)

    def __find_anonymous_member(self) -> Member:
        return Member.objects.filter(
            community=self.comm, user=self.anonymous_user).first()

    def test_join_success(self):
        self.__join_anonymus_to_link()

    def test_join_creates_member(self):
        comm = self.comm

        old_count = comm.members.count()
        self.__join_anonymus_to_link()

        comm.refresh_from_db()
        self.assertGreater(
            comm.members.count(), old_count,
            msg="members doesn't increased"
        )

        mem = self.__find_anonymous_member()
        self.assertIsNotNone(
            mem, 'member for user on join not created')

    def test_join_creates_conv(self):
        self.__join_anonymus_to_link()

        conv = Conversation.objects.filter(
            chat_id=self.comm.pk,
            user=self.anonymous_user).first()

        self.assertIsNotNone(
            conv, 'conv for member on join not created')

    def test_join_by_link(self):
        self.__join_anonymus_to_link()

        link = self.__find_anonymous_member().used_link

        self.assertIsNotNone(
            link, 'used_link for member is none')

        self.assertEqual(link, self.link.link)

    def test_join_by_guid(self):
        guid = 'iamthguid'
        self.comm.guid = guid
        self.comm.save()
        self.caller.post__join(self.anonymous_access, guid=guid)

        used_guid = self.__find_anonymous_member().used_guid
        self.assertIsNotNone(
            used_guid, 'used_guid for member is none')

        self.assertEqual(used_guid, guid)

    def test_join_on_already_joined(self):
        self.__join_anonymus_to_link()
        self.__join_anonymus_to_link(status.HTTP_400_BAD_REQUEST)

    def test_join_when_banned(self):
        self.__join_anonymus_to_link()
        self.caller.ban__member(
            self.access, self.anonymous_user.pk, self.comm)
        self.__join_anonymus_to_link(status.HTTP_400_BAD_REQUEST)

    def test_join_with_both_values(self):
        self.caller.post__join(
            self.anonymous_access, guid='imthguid',
            invite_link=self.link.link,
            allowed_status=status.HTTP_400_BAD_REQUEST
        )

    def test_join_with_bad_link(self):
        self.caller.post__join(
            self.anonymous_access,
            invite_link=generate_invite_link(),
            allowed_status=status.HTTP_400_BAD_REQUEST
        )

    def __leave_comm(self, access=None, comm=None,
                     status=status.HTTP_204_NO_CONTENT):
        self.caller.post__leave(
            access or self.normal_access,
            comm.pk if comm else self.comm.pk,
            allowed_status=status)

    def test_leave_deletes_member(self):
        self.__leave_comm()
        self.assertRaises(
            Member.DoesNotExist,
            self.normal_member.refresh_from_db)

    def test_leave_deletes_conv(self):
        self.__leave_comm()
        self.assertIsNone(
            Conversation.objects.filter(
                chat_id=self.comm.pk,
                user=self.normal_member.user
            ).first(),
            msg='member conv not deleted after leaving'
        )

    def test_leave_banned(self):
        banned_access, _ = self.__create_member_access(RANKS.BANNED)
        self.__leave_comm(banned_access,
                          status=status.HTTP_403_FORBIDDEN)

    def test_leave_owner_deletes_community(self):
        self.__leave_comm(self.access)
        self.assertIsNotNone(
            CommunityChat.objects
            .filter_deleted(pk=self.comm.pk)
            .first()
        )

    def test_leave_owner_deletes_members(self):
        comm_pk = self.comm.pk
        self.__leave_comm(self.access)
        self.assertFalse(
            Member.objects.filter(
                community_id=comm_pk
            ).exists(),
            msg="members not deleted after deleting community"
        )

    def test_leave_owner_deletes_convs(self):
        comm_pk = self.comm.pk
        self.__leave_comm(self.access)
        self.assertFalse(
            Conversation.objects.filter(
                chat_id=comm_pk
            ).exists(),
            msg="convs not deleted after deleting community"
        )
