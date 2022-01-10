
from django.core import validators
from django.utils.translation import gettext_lazy as _


class VerifyCodeValidator(validators.RegexValidator):
    regex = r'^\d{6}$'
    message = _(
        'Invalid code. code must be 6-digit number. e.g 123456'
    )
