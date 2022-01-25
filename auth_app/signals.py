from django.db.models.signals import post_save
from django.dispatch import receiver

from .tasks import delete_verifycode
from .models import VerifyCode


@receiver(post_save, sender=VerifyCode)
def add_delete_verifycode_task(sender, instance,
                               created, **kwargs):
    if created:
        countdown = instance.expire_after.seconds + 1
        delete_verifycode.apply_async([instance.pk],
                                      countdown=countdown)
