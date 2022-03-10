from rest_framework import viewsets, mixins

from django_filters.rest_framework.backends import DjangoFilterBackend

from core.paginations import DefaultLimitOffsetPagination
from core.filters import OrderingFilterWithSchema

from .queryset import get_chat_messages
from .serializers import MessageInfoSerializer
from .filters import MessageFilter


class MessageViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):

    serializer_class = MessageInfoSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilterWithSchema]
    filterset_class = MessageFilter
    pagination_class = DefaultLimitOffsetPagination
    ordering_fields = ['sent_at', '-sent_at']

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        return get_chat_messages(chat_id, self.request.user.pk)

    def get_object(self):
        return super().get_object()
