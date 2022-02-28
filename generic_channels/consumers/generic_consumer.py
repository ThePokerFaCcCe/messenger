from typing import Callable, Iterable, Optional, Union
from dotmap import DotMap
from asgiref.sync import async_to_sync
from django.utils.translation import gettext_lazy as _
from channels.generic.websocket import JsonWebsocketConsumer
from channels.exceptions import DenyConnection, InvalidChannelLayerError
from rest_framework.exceptions import APIException

from generic_channels.serializers import ConsumerContentSerializer
from ..exceptions import ConsumerException, PermissionDenied, ValidationError


class ChannelGroupsMixin:
    def __call_layer(self, func: Callable, *fargs, **fkwargs):
        """
        Call channel_layer methods in synchronous mode
        and check for errors
        """
        try:
            return async_to_sync(func)(*fargs, **fkwargs)
        except AttributeError:
            raise InvalidChannelLayerError(
                "BACKEND is unconfigured or doesn't support groups"
            )

    def group_join(self, group_name: str):
        """Join channel to a group"""
        group_name = str(group_name)
        if group_name in self.groups:
            return
        self.__call_layer(self.channel_layer.group_add,
                          group_name, self.channel_name)
        self.groups.append(group_name)

    def group_leave(self, group_name: str):
        """Remove channel from a group"""
        group_name = str(group_name)
        if group_name not in self.groups:
            return
        self.__call_layer(self.channel_layer.group_discard,
                          group_name, self.channel_name)
        self.groups.remove(group_name)

    def groups_join(self, group_names: Iterable[str]):
        """Join channel to list of groups"""
        for group in group_names:
            self.group_join(group)


class GenericConsumer(ChannelGroupsMixin, JsonWebsocketConsumer):
    '''
    Sent data by user should look like this example:
    ```
    {
        "action" : "action_name",
        "body"   : {"k1":"v1", "k2":{...}, ...},
        "query"  : {"k1":"v1",...},
    }
    ```
    '''
    class GlobalActions:
        CONNECT = '__connect__'
    __default_error_messages = {
        'unexpected': _("An unexpected error occured"),
        "action_404": _("Action not found"),
        "404": "{item} Not found",
    }
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

    def fail(self, detail_key: str = None,
             detail: str = None, action=None, *fargs, **fkwargs):
        """
        Call `.error()` method with either `detail_key` that found in 
        `default_error_messages` or `detail` string and raises exception
        """
        _kwargs = [detail, detail_key]
        assert not all(_kwargs) and any(_kwargs), (
            "You should set only one of `detail` or `detail_key` kwargs "
            f"in `{self.__class__.__name__}`"
        )
        if detail_key:
            detail = self.default_error_messages.get(detail_key, None)
            assert detail is not None, (
                f"detail_key of `{detail_key}` not found in "
                f"`default_error_messages` of `{self.__class__.__name__}`"
            )
        detail = detail.format(*fargs, **fkwargs)
        raise ValidationError(detail=detail, action=action)

    def success(self, content, detail: Union[str, dict] = None):
        """Send success message to client"""

        self.send_json({
            'action': content.get("action"),
            "status": "success",
            "detail": detail or None
        })

    def __handle_exception(self, func: Callable, *fargs, **fkwargs) -> bool:
        """
        Call function and handle some exceptions.
        returns True if no exceptions raised
        """
        try:
            func(*fargs, **fkwargs)
            return True
        except (APIException, ConsumerException) as e:
            self.error(e.detail)
        except Exception as e:
            self.error(self.default_error_messages.get("unexpected"))
            raise e

    def connect(self):
        super().connect()
        if not self.__handle_exception(
            self.has_permissions,
            self.GlobalActions.CONNECT, {}
        ):
            self.close(1008)
            raise DenyConnection()

    def close(self, code=None):
        return super().close(code)

    def validate_received_content(self, content) -> Optional[dict]:
        """Validate json content with serializer"""
        serializer = ConsumerContentSerializer(data=content)
        if not serializer.is_valid():
            return self.error(serializer.errors)
        return serializer.validated_data

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        """
        Validates text data and calls 
        `self.receive_json` with validated data
        """
        if text_data:
            content = self.validate_received_content(
                self.decode_json(text_data)
            )
            if content:
                self.receive_json(content, **kwargs)
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

    def receive_json(self, content: dict, **kwargs):
        """
        Receives validated json data from client
        and calls the action method
        """
        self.__handle_exception(
            self.call_action_method, content
        )

    def get_action(self, content: dict) -> Optional[str]:
        """Return the validated action of content

        e.g.: ChaT.message -> chat_message"""

        return content.get('action', '')\
            .replace('.', '_').lower()

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
            self.fail('action_404')
        self.has_permissions(action, content)

        method(content, action=action)

    def permission_denied(self, detail=None, action=None):
        """Raise `PermissionDenied` exception"""
        raise PermissionDenied(detail=detail, action=action)

    def get_permissions(self, action: str, content: dict) -> list:
        """Return list of permissions"""
        return [permission() for permission in self.permission_classes]

    def has_permissions(self, action: str, content: dict) -> bool:
        """Check for all permissions are allowed"""
        perms = self.get_permissions(action, content)
        if perms:
            for perm in perms:
                if not perm.has_permission(self.scope, self):
                    self.permission_denied(action=action)

    def get_serializer_context(self, action, content):
        """Return serializer's context"""

        return {
            'user': self.scope.user,
            'scope': self.scope,
            'consumer': self,

            # Added for compability with drf view serializers
            'request': self.scope,
            'view': self,
        }

    def get_serializer(self, action, content, *serializer_args,
                       **serializer_kwargs):
        """Call & return serializer"""

        serializer = self.get_serializer_class(action, content)
        if serializer:
            serializer_kwargs.setdefault(
                "context", self.get_serializer_context(action, content)
            )
            return serializer(*serializer_args, **serializer_kwargs)

    def get_serializer_class(self, action, content):
        """Return serializer class"""

        serializer = self.serializer_class
        assert serializer is not None, (
            "You have to set `serializer_class` attr or "
            "override `get_serializer` method in `%s` class"
            % self.__class__.__name__
        )

        return serializer
