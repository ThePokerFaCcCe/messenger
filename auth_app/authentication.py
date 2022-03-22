from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import TokenAuthentication

from .models import Access
from .utils import get_user_from_token, update_token_ip_address


class AccessTokenAuthentication(TokenAuthentication):
    model = Access

    def authenticate_credentials(self, key):
        model = self.get_model()

        token = model.objects.find_token(key, select=['user', 'device'])
        if not token or token.is_token_expired:
            raise AuthenticationFailed(_('Invalid token.'))

        user = get_user_from_token(token)
        if not user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))
        return (user, token)

    def authenticate(self, request):
        auth_result = super().authenticate(request)
        update_token_ip_address(
            token=auth_result[-1],
            request=request
        )
        return auth_result
