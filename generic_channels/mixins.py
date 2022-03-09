from typing import Callable, Iterable
from asgiref.sync import async_to_sync
from channels.exceptions import InvalidChannelLayerError


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


class DefaultEventsMixin:

    def event_send_message(self, event):
        """
        Remove 'type' key from event and set 'action'
        key to `GlobalActions.EVENT` send it to client
        """
        # BIG LESSON: Never remove "type" key from event!
        # event.pop("type", None)

        event['action'] = self.GlobalActions.EVENT
        self.send_json({k: v for k, v in event.items() if k != 'type'})

    def event_group_join(self, event):
        """Add consumer to given group"""

        if(name := event.get('group_name')):
            self.group_join(name)

    def event_group_leave(self, event):
        """Remove consumer from given group"""

        if(name := event.get('group_name')):
            self.group_leave(name)
