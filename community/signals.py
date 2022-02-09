from django.dispatch import receiver
from django.db.models.signals import post_save

from core.utils import delete_instance_on_error
from community.models import CommunityChat, Member
from community.tasks import create_member
from conversation.tasks import create_conversation


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
