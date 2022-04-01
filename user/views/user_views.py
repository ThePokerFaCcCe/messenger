from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from drf_spectacular.utils import extend_schema_view

from .mixins import UserProfileMixin
from core.permissions import IsAdminUserOR, IsOwnerOfItem
from user.schemas.views import USER_VIEW_SCHEMA
from user.serializers import (UserInfoSerializer,
                              UserUpdateSerializer,
                              UserStaffUpdateSerializer,
                              UserLastSeenSerializer,
                              UserProfileSerializer)
from global_id.views.mixins import GUIDCRUDMixin

User = get_user_model()


@extend_schema_view(**USER_VIEW_SCHEMA)
class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  UserProfileMixin,
                  GUIDCRUDMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserInfoSerializer
    lookup_value_regex = r'[\d]+'

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            if self.request.user.is_staff:
                return UserStaffUpdateSerializer
            return UserUpdateSerializer
        elif self.action == 'last_seen':
            return UserLastSeenSerializer
        elif self.action == 'profile_image':
            return UserProfileSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if (self.action in ['update', 'partial_update']
                    or (self.action == 'profile_image'
                        and self.request.method != 'GET'
                        )
                ):
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
                      UserProfileMixin,
                      GUIDCRUDMixin,
                      viewsets.GenericViewSet):
    serializer_class = UserInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        if self.action == 'send_alive':
            return UserLastSeenSerializer
        if self.action == 'profile_image':
            return UserProfileSerializer

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
