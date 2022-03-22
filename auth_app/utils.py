from ipware import get_client_ip

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
    token.update_last_used(save=False)
    if request:
        ip, routable = get_client_ip(request)
    else:
        ip = scope.get("client", [None])[0]
    if ip:
        token.ip = ip
    token.save()
