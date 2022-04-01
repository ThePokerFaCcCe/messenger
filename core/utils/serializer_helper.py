from typing import Optional
from django.db.models import Model


def get_context_user(context) -> Optional[Model]:
    """
    Get user from serializer's context, if 'view' not found in `context`,
    or if one of 'request' or 'scope' attrs not found in 'view',
    `AttributeError` will be raised.

    if user not found, or found but not authenticated, `None` will be returned.
    """
    view = context.get('view')
    if not view:
        raise AttributeError("`view` attr not found in context")

    if hasattr(view, "request"):
        user = view.request.user
    elif hasattr(view, "scope"):
        user = view.scope.get("user")
    else:
        raise AttributeError("`request` or `scope` attr not found in view")

    if not (user and user.is_authenticated):
        return None

    return user
