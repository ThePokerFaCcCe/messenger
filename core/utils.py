from uuid import uuid4


def generate_email(domain="gmail.com") -> str:
    """Create random email with uuid"""
    return f'{uuid4()}@{domain}'
