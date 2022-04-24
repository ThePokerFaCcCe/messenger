from core.utils import generate_email
from user.models import Device, User, Contact


def create_user(email=None, **kwargs) -> User:
    email = email or generate_email()
    return User.objects.create_user(email, **kwargs)


def create_active_user(**kwargs) -> User:
    return create_user(is_active=True, **kwargs)


def create_device(user=None, type=Device.TypeChoices.WINDOWS,
                  model='10 Pro', **kwargs) -> Device:
    user = user or create_user()
    return Device.objects.create(user=user, type=type, model=model, **kwargs)


def create_contact(user=None, contacted_user=None, first_name='name', **kwargs) -> Contact:
    return Contact.objects.create(
        first_name=first_name,
        user=user or create_user(),
        contacted_user=contacted_user or create_user(),
        **kwargs)
