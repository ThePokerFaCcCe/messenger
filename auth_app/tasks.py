from celery import shared_task as task

from .models import VerifyCode


@task
def delete_verifycode(pk):
    VerifyCode.objects.filter(pk=pk, is_used=False).delete()
