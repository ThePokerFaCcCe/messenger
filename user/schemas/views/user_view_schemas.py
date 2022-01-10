from drf_spectacular.utils import OpenApiExample
from rest_framework import serializers
from user.serializers import UserStaffUpdateSerializer, UserSerializer
from core.schema_helper import schema_generator

userstaff_meta = UserStaffUpdateSerializer.Meta
user_meta = UserSerializer.Meta


class UserStaffUpdateRequestSchemaSerializer(
        serializers.ModelSerializer):
    class Meta:
        model = userstaff_meta.model
        fields = list(set(userstaff_meta.fields[1:])
                      - set(userstaff_meta.read_only_fields))


class UserUpdateRequestSchemaSerializer(
        serializers.ModelSerializer):
    class Meta:
        model = user_meta.model
        fields = list(set(user_meta.fields[1:])
                      - set(user_meta.read_only_fields))


STAFF_UPDATE_REQUEST_EXAMPLE = OpenApiExample(
    name='Staff update',
    request_only=True,
    value=schema_generator(UserStaffUpdateRequestSchemaSerializer().fields)
)

USER_UPDATE_REQUEST_EXAMPLE = OpenApiExample(
    name='User update',
    request_only=True,
    value=schema_generator(UserUpdateRequestSchemaSerializer().fields)
)
