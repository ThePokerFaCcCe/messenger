from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view

from core.permissions import IsAdminUserOR, IsOwnerOfItem
from user.schemas.views import USER_VIEW_SCHEMA
from user.serializers import (UserSerializer,
                              UserStaffUpdateSerializer,
                              UserLastSeenSerializer)


User = get_user_model()


@extend_schema_view(**USER_VIEW_SCHEMA)
class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_value_regex = r'[\d]+'

    def get_serializer_class(self):
        if (self.action in ['update', 'partial_update']
                and self.request.user.is_staff):
            return UserStaffUpdateSerializer
        elif self.action == 'last_seen':
            return UserLastSeenSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [perm() for perm in [IsOwnerOfItem | IsAdminUserOR]]
        return [permissions.IsAuthenticated()]

    @action(["get"], detail=True, url_path=r'last-seen')
    def last_seen(self, request, *args, **kwargs):
        """Get user's last seen and online status"""
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(**USER_VIEW_SCHEMA)
class SelfUserViewSet(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    # queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'send_alive':
            return UserLastSeenSerializer

        return super().get_serializer_class()

    def get_object(self):
        user = self.request.user
        if not (user and user.is_authenticated):
            raise NotFound()

        return user

    @action(["post"], detail=False, url_path=r'send-alive')
    def send_alive(self, request, *args, **kwargs):
        """Update user's `last_seen` to now"""
        user = self.get_object()
        user.set_online(save=True)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
