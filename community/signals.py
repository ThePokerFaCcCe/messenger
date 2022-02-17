from django.dispatch import receiver
from django.db import transaction
from django.db.models.signals import post_save, post_delete

from core.utils import delete_instance_on_error
from core.signals import post_soft_delete
from community.models import CommunityChat, Member
from community.tasks import create_member, delete_community_members
from conversation.tasks import create_conversation, delete_conversation


# from core.utils import check_task_failed
# @receiver(..., sender=...)
# def maybe_used_later(_,instance,created,**kwargs):
#     if created:
#         task = ....delay()
#         check_task_failed(task, True, [instance])

@receiver(post_save, sender=CommunityChat)
def create_owner_member(sender, instance: CommunityChat,
                        created, **kwargs):
    if created:
        delete_instance_on_error(
            create_member, instance=instance,
            community_id=instance.pk,
            user_id=instance.creator.pk,
            rank=Member.RankChoices.OWNER
        )


@receiver(post_save, sender=Member)
def create_member_conversation(sender, instance: Member,
                               created, **kwargs):
    if created:
        delete_instance_on_error(
            create_conversation, instance=instance,
            chat=instance.community,
            user_id=instance.user.pk
        )


@transaction.atomic
@receiver(post_delete, sender=Member)
def delete_member_conversation(sender, instance: Member, **kwargs):
    delete_conversation(chat_id=instance.community_id,
                        user_id=instance.user_id)
    if (instance.rank == Member.RankChoices.OWNER
            and not instance.community.is_deleted
        ):
        instance.community.soft_delete()


@transaction.atomic
@receiver([post_soft_delete, post_delete], sender=CommunityChat)
def delete_conversation_members(sender, instance: CommunityChat, **kwargs):
    uids = delete_community_members(community_id=instance.pk)
    delete_conversation(chat_id=instance.pk, user_id=uids)
