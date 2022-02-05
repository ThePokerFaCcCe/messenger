from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, viewsets, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from conversation.models import Conversation
from conversation.serializers import (
    ConversationSerializer, ConversationPinSerializer,
    ConversationArchiveSerializer, ConversationAliasSerializer,
    ConversationUpdateSerializer)


class ConversationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):

    serializer_class = ConversationSerializer

    def get_queryset(self):
        qs = Conversation.objects.all()

        if self.action in ['retrieve', 'list']:
            qs = qs.auto_prefetch_next()

        return qs.filter(
            user=self.request.user
        )

    def get_serializer_class(self):
        if self.action in ['pin', 'unpin']:
            return ConversationPinSerializer
        if self.action in ['archive', 'unarchive']:
            return ConversationArchiveSerializer
        if self.action in ['update', 'partial_update']:
            return ConversationUpdateSerializer
        if self.action == 'alias':
            return ConversationAliasSerializer

        return super().get_serializer_class()

    def _pin(self, should_pin
             ) -> ConversationPinSerializer:
        conv: Conversation = self.get_object()

        if should_pin and conv.is_pinned:
            raise exceptions.ValidationError(
                _("Conversation is already pinned")
            )
        elif not should_pin and not conv.is_pinned:
            raise exceptions.ValidationError(
                _("Conversation is not pinned")
            )

        conv.is_pinned = should_pin
        conv.save()
        return self.get_serializer(conv)

    def _archive(self, should_archive
                 ) -> ConversationArchiveSerializer:
        conv: Conversation = self.get_object()

        if should_archive and conv.is_archived:
            raise exceptions.ValidationError(
                _("Conversation is already archived")
            )
        elif not should_archive and not conv.is_archived:
            raise exceptions.ValidationError(
                _("Conversation is not archived")
            )

        conv.is_archived = should_archive
        conv.save()
        return self.get_serializer(conv)

    @action(['post'], detail=True)
    def pin(self, *args, **kwargs):
        serializer = self._pin(should_pin=True)
        return Response(data=serializer.data)

    @action(['post'], detail=True)
    def unpin(self, *args, **kwargs):
        serializer = self._pin(should_pin=False)
        return Response(data=serializer.data)

    @action(['post'], detail=True)
    def archive(self, *args, **kwargs):
        serializer = self._archive(should_archive=True)
        return Response(data=serializer.data)

    @action(['post'], detail=True)
    def unarchive(self, *args, **kwargs):
        serializer = self._archive(should_archive=False)
        return Response(data=serializer.data)

    @action(['post'], detail=True)
    def alias(self, request, *args, **kwargs):
        conv = self.get_object()
        serializer = self.get_serializer(conv, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data)
