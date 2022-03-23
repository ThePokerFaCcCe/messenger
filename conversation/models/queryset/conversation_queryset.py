from django.db.models.query import prefetch_related_objects
from django.db.models import QuerySet

import conversation.models.conversation as conversation


class ConversationQuerySet(QuerySet):
    __prefetch_next = False

    def auto_prefetch_next(self):
        """calls necessary `.prefetch_related` methods
        on next `.filter` call. that returns a list"""

        self.__prefetch_next = True
        return self

    def __prefetch_types(self, queryset):
        types = conversation.Conversation.TypeChoices

        pvs = []
        communities = []

        for conv in queryset:
            if conv.type == types.PRIVATE:
                pvs.append(conv)
            else:
                communities.append(conv)

        prefetch_related_objects(
            pvs, 'chat__users', 'chat__creator'
        )

        prefetch_related_objects(
            communities, 'chat__creator')

    def filter(self, *args, **kwargs):
        """if `.auto_prefetch_next` method was called before,
        necessary prefetch_relateds will be called"""

        queryset = super().filter(*args, **kwargs)
        if self.__prefetch_next:
            self.__prefetch_next = False

            self.__prefetch_types(queryset)

        return queryset
