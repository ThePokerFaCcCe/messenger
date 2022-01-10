from rest_framework import serializers
from django.contrib.auth import get_user_model

from auth_app.models import VerifyCode
from core.serializers.mixins import NormalizeEmailSerializerMixin

User = get_user_model()


class CreateVerifyCodeSerializer(NormalizeEmailSerializerMixin,
                                 serializers.ModelSerializer):
    default_error_messages = {
        "active_found": "Active verify code for email {email}"
                        " found. try again after {expire}"
    }

    email = serializers.EmailField()
    expires_at = serializers.DateTimeField(read_only=True)
    message = serializers.CharField(read_only=True,
                                    default='Code sent to your email')
    user = serializers.HiddenField(default=None)

    class Meta:
        model = VerifyCode
        fields = [
            'user',
            'email',
            'message',
            'expires_at',
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)

        email = attrs.pop('email')
        user, is_created = User.objects.get_or_create(email=email)

        queryset = self.context.get("view").get_queryset()
        if not is_created and (
                code := queryset.filter(user=user).first()
        ):
            self.fail('active_found', email=email, expire=code.expires_at)

        attrs['user'] = user
        return attrs


code_length = VerifyCode.max_digit


class CheckVerifyCodeSerializer(NormalizeEmailSerializerMixin,
                                serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    code = serializers.RegexField(write_only=True,
                                  regex=VerifyCode.validation_regex,
                                  max_length=code_length,
                                  min_length=code_length)


class TokenVerifyCodeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = VerifyCode
        fields = [
            'email',
            'token',
        ]
        extra_kwargs = {
            'token': {"source": "encrypted_token"},
        }
