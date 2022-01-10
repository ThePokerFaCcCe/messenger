from typing import Any, Callable
from rest_framework.exceptions import NotFound


class GetObjectByTokenMixin:
    """Mixin for finding instance from token that user 
    will send it in url parameters"""

    find_token_func: Callable = None
    """Function that used for finding token"""

    find_token_func_kwargs: dict[str, Any] = {}
    """kwargs that should be passed to function"""

    lookup_field = 'token'

    def get_object(self):
        """Returns instance that got from 
        `self.find_token_func` with value of 
        `self.lookup_field`, if instance was `None`, 
        `NotFound` exception will be raised."""

        token = self.kwargs.get(self.lookup_field)
        instance = self.find_token_func(
            token, **self.find_token_func_kwargs
        )

        if not instance:
            raise NotFound()
        return instance


class GetBodyTokenObjectMixin:
    """Mixin for finding instance from token that user 
    will send it in request body"""

    body_token_lookup: str = None
    """key in `request.body` that contains body token"""

    body_token_find_func: Callable = None
    """Function that used for finding body token"""

    body_token_find_func_kwargs: dict[str, Any] = {}
    """kwargs that should be passed to function"""

    def get_body_token_object(self, expire_field: str = "is_token_expired"):
        """Returns instance that got from 
        `self.body_token_find_func` with value of 
        `self.body_token_lookup`, if instance was `None`, 
        `NotFound` exception will be raised.

        Parameters
        ----------
        `expire_field` : field that if was `True`, `NotFound` will be raised,
        default value is 'is_token_expired' that is for `BaseToken`
        """

        token = self.request.data.get(self.body_token_lookup)
        instance = self.body_token_find_func(
            token, **self.body_token_find_func_kwargs
        )
        if not instance or getattr(instance, expire_field, False):
            raise NotFound({self.body_token_lookup: 'not found'})
        return instance
