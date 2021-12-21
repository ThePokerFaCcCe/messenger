import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r'^[A-Za-z]{1,}[_]?[A-Za-z0-9]{1,}$'
    message = _(
        'Invalid username. username must start with a-z, A-Z '
        'and can contain a-z, A-Z, 0-9 and one underscore( _ )'
    )
    flags = re.ASCII


class VerifyCodeValidator(validators.RegexValidator):
    regex = r'^\d{6}$'
    message = _(
        'Invalid code. code must be 6-digit number. e.g 123456'
    )
