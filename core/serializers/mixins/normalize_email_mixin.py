from user.models.user import User


class NormalizeEmailSerializerMixin:
    def validate(self, attrs):
        attrs["email"] = User.objects.normalize_email(
            attrs.get('email'))

        return super().validate(attrs)
