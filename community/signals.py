from django.dispatch import receiver
from django.db.models.signals import post_save

from core.utils import check_task_failed
from community.models import CommunityChat, Member
from community.tasks import create_member
from conversation.tasks import create_conversation


@receiver(post_save, sender=CommunityChat)
def create_owner_member(sender, instance: CommunityChat,
                        created, **kwargs):
    if created:
        member_task = create_member.delay(
            community_id=instance.pk,
            user_id=instance.creator.pk,
            rank=Member.RankChoices.OWNER
        ).get(propagate=False)

    check_task_failed(member_task, True, [instance])


@receiver(post_save, sender=Member)
def create_member_conversation(sender, instance: Member,
                               created, **kwargs):
    if created:
        conv_task = create_conversation(
            chat=instance.community,
            user_id=instance.user.pk
        ).get(propagate=False)
        check_task_failed(conv_task, True, [instance])
