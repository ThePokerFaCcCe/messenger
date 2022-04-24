from django.conf import settings
from ipware import get_client_ip
from django.utils import timezone

from .models import Access


def get_user_from_token(token: Access):
    user = token.user
    setattr(user, 'used_access', token)
    setattr(user, 'used_device', token.device)
    return user


def update_token_information(token: Access, request=None, scope=None):
    assert not all([request, scope]) and any([request, scope]), (
        "Only one of `request` or `scope` should set"
    )

    if request:
        ip = get_client_ip(request)[0]
    else:
        ip = scope.get("client", [None])[0]

    interval = getattr(settings, 'UPDATE_AUTH_TOKEN_INFO_INTERVAL',
                       timezone.timedelta(seconds=2))
    if ((timezone.now() - token.last_used) < interval) and ip == token.ip:
        return

    token.ip = ip
    token.update_last_used(save=False)
    token.save()
