from uuid import uuid4

from user.models import Device, User, VerifyCode
from user.models.access import Access


def generate_email(domain="gmail.com") -> str:
    """Create random email with uuid"""
    return f'{uuid4()}@{domain}'


def create_user(email=None, **kwargs) -> User:
    email = generate_email() if not email else email
    return User.objects.create_user(email, **kwargs)


def create_verifycode(user=None, **kwargs) -> VerifyCode:
    user = create_user() if not user else user
    code = VerifyCode.objects.create(user=user, **kwargs)
    code.refresh_from_db()
    return code


def create_device(user=None, type=Device.TypeChoices.WINDOWS,
                  model='10 Pro', **kwargs) -> Device:
    user = create_user() if not user else user
    return Device.objects.create(user=user, type=type, model=model, **kwargs)


def create_access(user=None, device=None, **kwargs) -> Device:
    user = create_user() if not user else user
    device = create_device(user) if not device else device
    return Access.objects.create(user=user, device=device, **kwargs)
