from uuid import uuid4
from random import randint

INVITE_LINK_MAX_LENGTH = 37  # len(generate_invite_link())
INVITE_LINK_REGEX = r'^([-])[A-Za-z\d]{32}([\d]{4})$'


def generate_invite_link():
    return f"-{uuid4().hex}{randint(1111,9999)}"
