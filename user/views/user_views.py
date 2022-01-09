from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, permissions
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema_view, extend_schema

from core.permissions import IsAdminUserOR, IsOwnerOfItem
from user.schemas.views import (STAFF_UPDATE_REQUEST_EXAMPLE,
                                USER_UPDATE_REQUEST_EXAMPLE)
from user.serializers import UserSerializer, UserStaffUpdateSerializer


User = get_user_model()

update_schema = extend_schema(
    description=("Update user information"),
    examples=[USER_UPDATE_REQUEST_EXAMPLE, STAFF_UPDATE_REQUEST_EXAMPLE],
    responses={200: UserSerializer,
               400: None, 404: None}
)


@extend_schema_view(
    retrieve=extend_schema(
        description=("Show user information"),
        responses={200: UserSerializer,
                   400: None, 404: None}
    ),
    update=update_schema,
    partial_update=update_schema
)
class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if (self.action in ['update', 'partial_update']
                and self.request.user.is_staff):
            return UserStaffUpdateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [perm() for perm in [IsOwnerOfItem | IsAdminUserOR]]
        return [permissions.IsAuthenticated()]

    def get_instance(self):
        return self.request.user

    @action(["get", "put", "patch"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)
