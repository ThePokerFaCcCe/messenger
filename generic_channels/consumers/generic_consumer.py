import re
from traceback import print_tb
from typing import Callable, Optional, Union
from dotmap import DotMap
from django.utils.translation import gettext as _
from channels.generic.websocket import JsonWebsocketConsumer
from channels.exceptions import DenyConnection
from rest_framework.exceptions import APIException

from generic_channels.serializers import ConsumerContentSerializer
from ..exceptions import ConsumerException, PermissionDenied, ValidationError
from ..mixins import ChannelGroupsMixin, DefaultEventsMixin


class GenericConsumer(ChannelGroupsMixin, DefaultEventsMixin,
                      JsonWebsocketConsumer):
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
        EVENT = '__event__'
    __default_error_messages = {
        'unexpected': _("An unexpected error occured"),
        "action_404": _("Action not found"),
        "404": "{item} Not found",
    }
    default_error_messages = {}
    permission_classes = []
    serializer_class = None
    filter_query_lookup = 'pk'

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
            print_tb(e.__traceback__)
            print(e)
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
                content = DotMap(content)
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
        self.validate_action_query_params(content, action, method)
        self.has_permissions(action, content)
        method(content, action=action)

    def validate_action_query_params(self, content, action, action_method: Callable):
        """Validate query params that exist in content's query key"""
        q_params = getattr(action_method, 'query_params', None)
        if not q_params:
            return
        errors = {}
        depends = {}
        q_content = content.query
        for k, v in q_params.items():
            if k not in q_content:
                errors[k] = f'should be in query data'
                continue

            if (kregex := v.get("regex")):
                if not re.match(kregex, str(q_content[k])):
                    errors[k] = f'isn\'t a valid value'
                    continue

            if (ktype := v.get('type')):
                try:
                    val = ktype(q_content[k])
                    q_content[k] = val
                except ValueError:
                    errors[k] = f'isn\'t a valid value'
                    continue

            if (kvalidator := v.get('validator')):
                stats, val = kvalidator(q_content[k], self)
                if not stats:
                    errors[k] = val
                    continue
                q_content[k] = val

            if (queryset := v.get('queryset')):
                lookup = v.get('lookup') or self.filter_query_lookup
                qs = queryset.filter(**{lookup: q_content[k]})
                if (v_depends := v.get('depends')):
                    depends[k] = {'qs': qs, 'depends': v_depends}
                else:
                    if not qs.exists():
                        errors[k] = f'not found'
                        continue
                    obj = qs.first()
                    self.has_object_permissions(action, content, obj)
                    q_content[f"{k}_queryset"] = qs
                    q_content[f"{k}_object"] = obj

        if not errors and depends:
            for k, v in depends.items():

                qs = v["qs"]
                for lookup in v['depends']:
                    qs = qs.filter(**{lookup: q_content.get(lookup)})

                if not qs.exists():
                    errors[k] = f'not found'
                    continue
                obj = qs.first()
                self.has_object_permissions(action, content, obj)
                q_content[f"{k}_queryset"] = qs
                q_content[f"{k}_object"] = obj

        if errors:
            self.fail(detail=errors, action=action)

    def permission_denied(self, detail=None, action=None):
        """Raise `PermissionDenied` exception"""
        raise PermissionDenied(detail=detail, action=action)

    def get_permissions(self, action: str, content: dict) -> list:
        """Return list of permissions"""
        return [permission() for permission in self.permission_classes]

    def has_permissions(self, action: str, content: dict):
        """Check for all permissions are allowed"""
        perms = self.get_permissions(action, content)
        if perms:
            for perm in perms:
                if not perm.has_permission((content | self.scope), self):
                    self.permission_denied(action=action)

    def has_object_permissions(self, action: str, content: dict, obj):
        """Check for all object permissions are allowed"""
        perms = self.get_permissions(action, content)
        if perms:
            for perm in perms:
                if not perm.has_object_permission((content | self.scope), self, obj):
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

    def validate_serializer(self, serializer, action=None):
        """
        Calls `.is_valid` method of serializer
        and raises exception if serializer isn't valid
        """
        if not serializer.is_valid():
            raise ValidationError(serializer.errors, action=action)
