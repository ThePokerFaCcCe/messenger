from core.utils import generate_email
from user.models import Device, User


def create_user(email=None, **kwargs) -> User:
    email = generate_email() if not email else email
    return User.objects.create_user(email, **kwargs)


def create_device(user=None, type=Device.TypeChoices.WINDOWS,
                  model='10 Pro', **kwargs) -> Device:
    user = create_user() if not user else user
    return Device.objects.create(user=user, type=type, model=model, **kwargs)
