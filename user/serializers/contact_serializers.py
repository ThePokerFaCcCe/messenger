from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from user.models import Contact

User = get_user_model()


class ContactCreateSerializer(serializers.ModelSerializer):
    default_error_messages = {
        'email_404': _("User with this email not found"),
        'email_exists': _("This email is in your contacts"),
    }
    email = serializers.EmailField(write_only=True)
    contacted_user = serializers.HiddenField(default=0)
    user = serializers.HiddenField(default=0)
    email_user = None

    class Meta:
        model = Contact
        fields = [
            'first_name',
            'last_name',
            'email',
            'contacted_user',
            'user',
        ]

    def validate_email(self, value):
        email_user = User.objects.filter(email=value).first()
        if not email_user:
            self.fail('email_404')

        contact = Contact.objects.filter(
            user=self.context['request'].user,
            contacted_user=email_user
        )
        if contact.exists():
            self.fail("email_exists")

        self.email_user = email_user
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs.pop("email")
        attrs['contacted_user'] = self.email_user
        attrs['user'] = self.context['request'].user
        return attrs


class ContactUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'first_name',
            'last_name',
        ]
