from rest_framework import viewsets, mixins, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view

from auth_app.models import Access
from auth_app.schemas import AccessCreateSchemaSerializer
from auth_app.serializers import AccessCreateSerializer, AccessInfoSerializer
from user.models import Device
from core.views.mixins import (GetBodyTokenObjectMixin,
                               GetObjectByTokenMixin)


@extend_schema_view(
    create=extend_schema(
        description=("Create accress token for user and device "
                     "(user and device will find from "
                     "`device_token`) and return access `token` "
                     "that can be used for authorization."
                     ),
        request=AccessCreateSchemaSerializer,
        responses={200: AccessCreateSerializer,
                   400: None, 404: None}
    ),
    retrieve=extend_schema(
        description=("Find a access from it's `token`"),
        responses={200: AccessInfoSerializer,
                   400: None, 404: None}
    )
)
class AccessViewSet(GetObjectByTokenMixin,
                    GetBodyTokenObjectMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = Access.objects.all()  # .select_related('device')

    find_token_func = Access.objects.find_token
    find_token_func_kwargs = {'select': ['device']}

    body_token_lookup = "device_token"
    body_token_find_func = Device.objects.find_token
    # body_token_find_func_kwargs = {'select': ['user']}

    def get_queryset(self):
        return super().get_queryset().filter(
            user=self.request.user
        ).select_related("device")

    def get_serializer_class(self):
        if self.action == 'create':
            return AccessCreateSerializer
        return AccessInfoSerializer

    def perform_create(self, serializer):
        device: Device = self.get_body_token_object()
        serializer.save(user=device.user, device=device)
        device.is_token_expired = True
        device.save()

    def get_permissions(self):
        if self.action != 'create':
            return [permissions.IsAuthenticated()]
