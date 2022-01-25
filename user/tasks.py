from celery import shared_task as task

from django.contrib.auth import get_user_model
from auth_app.models import VerifyCode
User = get_user_model()


@task
def delete_inactive_users():
    """Delete inactive users that haven't active verifycode"""
    all_inactive_users = User.objects.all().filter(is_active=False)
    active_vcode_users = VerifyCode.objects.select_related('user')\
        .filter_unexpired().filter(user__in=all_inactive_users)\
        .values_list("user", flat=True)

    inactives = all_inactive_users.exclude(pk__in=active_vcode_users)
    inactives.delete()
