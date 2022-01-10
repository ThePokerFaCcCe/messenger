from rest_framework import viewsets, mixins, status
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from auth_app.models import VerifyCode
from auth_app.serializers import (CheckVerifyCodeSerializer,
                                  CreateVerifyCodeSerializer,
                                  TokenVerifyCodeSerializer)


@extend_schema_view(
    create=extend_schema(
        responses={
            200: CreateVerifyCodeSerializer,
            400: None,
            404: None,
        }
    ),
    check=extend_schema(
        responses={
            200: TokenVerifyCodeSerializer,
            400: None,
            404: None,
        }
    ),
)
class VerifyCodeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    http_method_names = ('post', 'options', 'head')

    def get_serializer_class(self):
        if self.action == 'check':
            return CheckVerifyCodeSerializer
        return CreateVerifyCodeSerializer

    def get_queryset(self):
        qs = VerifyCode.objects.filter_unexpired()
        if self.action == 'check':
            return qs.select_related("user")
        return qs

    def create(self, request, *args, **kwargs):
        """Create verify code and send to entered `email`.
        the code will expire after `expires_at`"""
        serializer = self.get_serializer(data=request.data)

        with transaction.atomic():
            serializer.is_valid(raise_exception=True)
            code: VerifyCode = serializer.save()
            code.email_code()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['post'])
    def check(self, request, *args, **kwargs):
        """Check entered `code` for `email`,
        if data was correct, user will be active 
        and `token` will return, 
        that can be used for creating device"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        verifycode: VerifyCode = self.get_queryset().filter(
            user__email=email,
        ).first()

        if not verifycode:
            raise NotFound(detail='No active code found')

        code_number = serializer.validated_data.get("code")
        if not verifycode.check_code(code_number):
            verifycode.increase_tries(save=True)
            raise NotFound(detail='No active code found')
            # raise ValidationError({'code': "Code is not correct"})

        verifycode.is_used = True
        verifycode.save()

        verifycode.user.is_active = True
        verifycode.user.save()

        serializer = TokenVerifyCodeSerializer(verifycode)
        return Response(serializer.data)
