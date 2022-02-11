from django.utils.functional import cached_property
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins, permissions
from rest_framework.decorators import action

from core.views.mixins import NestedViewMixin
from community.serializers import GroupRulesSerializer
from community.permissions import IsCommunityAdminMember, IsCommunityNormalMember
from community.models import (GroupRules, CommunityChat)


class RulesNestedViewSet(mixins.UpdateModelMixin,
                         mixins.RetrieveModelMixin,
                         NestedViewMixin,
                         viewsets.GenericViewSet):

    nested_queryset = CommunityChat.objects\
        .prefetch_related('community__rules')

    nested_lookup_field = 'community_id'

    def get_object(self):
        return self.nested_object.community.rules

    def get_serializer_class(self):
        rule = self.get_object()
        if isinstance(rule, GroupRules):
            return GroupRulesSerializer
        raise AssertionError(
            f"Unsupported rule type in {self.__class__.__name__}")

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsCommunityAdminMember()]
        return [IsCommunityNormalMember()]
