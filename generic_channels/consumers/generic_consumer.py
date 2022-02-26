from typing import Callable, Optional, Union
from functools import lru_cache
from dotmap import DotMap
import re
from django.utils.translation import gettext_lazy as _
from channels.generic.websocket import JsonWebsocketConsumer
from channels.exceptions import DenyConnection


@lru_cache(maxsize=30)
def validate_regex(text, regex=r'^[\w]+$') -> bool:
    return bool(re.match(regex, text))


class GenericConsumer(JsonWebsocketConsumer):
    class GlobalActions:
        CONNECT = '__connect__'
    __default_error_messages = {
        'unexpected': _("An unexpected error occured"),
        "action_404": _("Action not found"),
        'perm_denied': _("You don't have permissions to perform this action")
    }
    action_field = 'action'
    action_regex_validator = r'^[a-z]+[_.]?[a-z]+$'

    default_error_messages = {}
    serializer_class = None
    permission_classes = []

    __scope = None

    @property
    def scope(self):
        return self.__scope

    @scope.setter
    def scope(self, value):
        self.__scope = DotMap(value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_error_messages = (
            self.__default_error_messages
            | self.default_error_messages
        )

    def error(self, detail: Union[str, dict] = None):
        """Send error message to client"""

        self.send_json({
            "status": "error",
            "detail": detail or self.default_error_messages.get('unexpected', '')
        })

    def fail(self, detail_key: str, *fargs, **fkwargs):
        """Call `.error()` method with detail that found in 
        `default_error_messages`"""

        detail = self.default_error_messages.get(detail_key, None)
        assert detail is not None, (
            f"detail_key of `{detail_key}` not found in "
            f"`default_error_messages` of `{self.__class__.__name__}`"
        )
        detail = detail.format(*fargs, **fkwargs)
        self.error(detail)

    def connect(self):
        super().connect()
        if not self.has_permissions(self.GlobalActions.CONNECT, {}):
            self.close(1008)
            raise DenyConnection()

    def close(self, code=None):
        return super().close(code)

    def receive_json(self, content: dict, **kwargs):
        """Receives json data from client & calls the action method"""

        self.call_action_method(content)

    def validate_action(self, action_name: str) -> bool:
        """Validate action name with `action_regex_validator`"""
        return validate_regex(action_name, self.action_regex_validator)

    def get_action(self, content: dict) -> Optional[str]:
        """Return the validated action of content

        e.g.: ChaT.message -> chat_message"""

        action = content.get(self.action_field, '')\
            .replace('.', '_').lower()
        if self.validate_action(action):
            return action

    def get_action_method(self, content: dict) -> tuple[Optional[Callable], Optional[str]]:
        """Return action method if found. if action was `chat_send`, then 
        `action_chat_send` will be called.

        Returns tuple of `(method:callable|None, action:str|None)`
        """
        method = None
        action = self.get_action(content)
        if action:
            action_method_name = f"action_{action}"
            method = getattr(self, action_method_name, None)
        return (method, action)

    def call_action_method(self, content: dict):
        """Call action method with `content` as first argument
        if action found else send not found message to client"""

        method, action = self.get_action_method(content)
        if method is None:
            return self.fail('action_404')

        if not self.has_permissions(action, content):
            return

        method(content)

    def permission_denied(self, detail=None):
        self.error(detail) if detail \
            else self.fail('perm_denied')

    def get_permissions(self, action: str, content: dict) -> list:
        """Return list of permissions"""
        return [permission() for permission in self.permission_classes]

    def has_permissions(self, action: str, content: dict) -> bool:
        """Check for all permissions are allowed"""
        perms = self.get_permissions(action, content)
        if perms:
            for perm in perms:
                if not perm.has_permission(self.scope, self):
                    return self.permission_denied()
        return True

    def get_serializer_context(self, content):
        """Return serializer's context"""

        return {
            'user': self.scope.get('user')
        }

    def get_serializer(self, content, *serializer_args,
                       **serializer_kwargs):
        """Call & return serializer"""

        serializer = self.get_serializer_class(content)
        if serializer:
            serializer_kwargs.setdefault(
                "context", self.get_serializer_context(content)
            )
            return serializer(*serializer_args, **serializer_kwargs)

    def get_serializer_class(self, content):
        """Return serializer class"""

        serializer = self.serializer_class
        assert serializer is not None, (
            "You have to set `serializer_class` attr or "
            "override `get_serializer` method in `%s` class"
            % self.__class__.__name__
        )

        return serializer
