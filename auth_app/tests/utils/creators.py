from auth_app.models import Access, VerifyCode
from user.tests.utils import create_user, create_device


def create_verifycode(user=None, active_token=False, **kwargs) -> VerifyCode:
    user = create_user() if not user else user
    code = VerifyCode.objects.create(user=user, **kwargs)
    code.refresh_from_db()
    if active_token:
        code.is_used = True
        code.save()
    return code


def create_access(user=None, device=None,
                  activate_user=False, **kwargs) -> Access:
    user = create_user(is_active=activate_user) if not user else user
    device = create_device(user) if not device else device
    return Access.objects.create(user=user, device=device, **kwargs)
