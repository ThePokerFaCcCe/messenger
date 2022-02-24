from django.contrib.auth.models import AnonymousUser
from auth_app.models import Access
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware


@database_sync_to_async
def get_user(token_key):
    token = Access.objects.find_token(token_key, select=['user'])
    return token.user if token else AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            token_key = dict(scope['headers']).get(b"token").decode()
        except ValueError:
            token_key = None
        scope['user'] = AnonymousUser() if token_key is None else await get_user(token_key)

        return await super().__call__(scope, receive, send)
