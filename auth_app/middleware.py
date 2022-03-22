from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from .models import Access
from .utils import get_user_from_token, update_token_ip_address


@database_sync_to_async
def get_user(token_key):
    token = Access.objects.find_token(token_key, select=['user', 'device'])
    if not token:
        return None

    user = get_user_from_token(token)
    return (user, token)


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            token_key = dict(scope['headers']).get(b"token").decode()
        except (ValueError, AttributeError):
            token_key = None

        if token_key is None:
            user = AnonymousUser()
        elif (db_user := await get_user(token_key)):
            user, token = db_user
            await database_sync_to_async(
                update_token_ip_address
            )(token, scope=scope)

        scope['user'] = user
        return await super().__call__(scope, receive, send)
