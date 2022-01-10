from rest_framework import mixins, viewsets
from drf_spectacular.utils import extend_schema_view, extend_schema

from user.schemas.views import DeviceCreateSchemaSerializer
from user.models import Device
from auth_app.models import VerifyCode
from user.serializers import DeviceCreateSerializer, DeviceInfoSerializer
from core.views.mixins import GetObjectByTokenMixin, GetBodyTokenObjectMixin


@extend_schema_view(
    create=extend_schema(
        description=("Create a device for user (user will be "
                     "find from `verifycode_token`) and "
                     "return device's `token` that "
                     "can be used for creating `access token`s"
                     ),
        request=DeviceCreateSchemaSerializer,
        responses={200: DeviceCreateSchemaSerializer,
                   400: None, 404: None}
    ),
    retrieve=extend_schema(
        description=("Find a device from it's `token`"),
        responses={200: DeviceInfoSerializer,
                   400: None, 404: None}
    )
)
class DeviceViewSet(GetObjectByTokenMixin,
                    GetBodyTokenObjectMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    queryset = Device.objects.all()  # .select_related('user')

    find_token_func = Device.objects.find_token
    # find_token_func_kwargs = {'select': ['user']}

    body_token_lookup = "verifycode_token"
    body_token_find_func = VerifyCode.objects.find_token
    body_token_find_func_kwargs = {'select': ['user']}

    def get_serializer_class(self):
        if self.action == 'create':
            return DeviceCreateSerializer
        return DeviceInfoSerializer

    def perform_create(self, serializer):
        verifycode = self.get_body_token_object()
        serializer.save(user=verifycode.user)
        verifycode.is_token_expired = True
        verifycode.save()
