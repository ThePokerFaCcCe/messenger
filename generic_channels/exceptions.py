from django.utils.translation import gettext as _


class ConsumerException(Exception):
    detail: dict = None
    default_detail = _("An unexpected error occured")
    default_code = None

    def __init__(self, detail=None, code=None, action=None):
        detail = detail or self.default_detail
        if not isinstance(detail, (dict, list, tuple, set)):
            detail = [detail]
        self.detail = {
            'action': action,
            'code': code or self.default_code,
            'info': detail,
        }


class ValidationError(ConsumerException):
    default_code = 'invalid'


class PermissionDenied(ConsumerException):
    default_code = 'permission_denied'
    default_detail = _("You don't have permissions to perform this action")
