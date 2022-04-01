from rest_framework import serializers

from core.utils import get_context_user
from picturic.serializer_fields import PictureField
from user.models import User


class UserInfoSerializer(serializers.ModelSerializer):
    profile_image = PictureField(read_only=True)
    is_contact = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'bio',
            'full_name',
            'guid',
            'profile_image',
            'last_seen',
            'is_contact',
            'is_online',
            'is_staff',
            'is_scam',
            'type',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        user = get_context_user(self.context)
        if (not (user and hasattr(user, 'contacts'))
                or instance == user):
            return data

        contact_filter = list(filter(
            lambda c: c.contacted_user_id == instance.pk,
            user.contacts.all()
        ))

        if not contact_filter:
            return data

        contact = contact_filter[0]
        data['first_name'] = contact.first_name
        data['last_name'] = contact.last_name
        data['full_name'] = contact.full_name
        data['is_contact'] = True

        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    profile_image = PictureField(read_only=True)

    class Meta:
        model = User
        read_only_fields = [
            'full_name',
            'guid',
            'profile_image',
            'last_seen',
            'is_online',
            'is_staff',
            'type',
            'is_scam',
        ]
        fields = [
            'id',
            'first_name',
            'last_name',
            'bio',
        ] + read_only_fields


class UserStaffUpdateSerializer(serializers.ModelSerializer):
    profile_image = PictureField(read_only=True)

    class Meta:
        model = User
        read_only_fields = [
            'full_name',
            'guid',
            'profile_image',
            'last_seen',
            'is_online',
            'type',
        ]
        fields = [
            'id',
            'first_name',
            'last_name',
            'bio',
            'is_staff',
            'is_scam',
        ] + read_only_fields


class UserLastSeenSerializer(serializers.ModelSerializer):
    next_offline = serializers.DateTimeField()

    class Meta:
        model = User
        fields = [
            'id',
            'is_online',
            'next_offline',
            'last_seen',
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = PictureField()

    class Meta:
        model = User
        fields = [
            'profile_image',
        ]
