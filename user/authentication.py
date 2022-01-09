from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import TokenAuthentication

from user.models import Access


class AccessTokenAuthentication(TokenAuthentication):
    model = Access

    def authenticate_credentials(self, key):
        model = self.get_model()

        token = model.objects.find_token(key, select=['user', 'device'])
        if not token or token.is_token_expired:
            raise AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))
        user = token.user
        setattr(user, 'used_access', token)
        setattr(user, 'used_device', token.device)
        return (user, token)
