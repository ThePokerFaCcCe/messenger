from rest_framework import serializers

from picturic.serializer_fields import PictureField
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    profile_image = PictureField(read_only=True)

    class Meta:
        model = User
        read_only_fields = [
            'full_name',
            'profile_image',
            'last_seen',
            'is_online',
            'is_staff',
            'is_bot',
            'is_scam',
        ]
        fields = [
            'id',
            'first_name',
            'last_name',
            'bio',
            'username',
        ] + read_only_fields


class UserStaffUpdateSerializer(serializers.ModelSerializer):
    profile_image = PictureField(read_only=True)

    class Meta:
        model = User
        read_only_fields = [
            'full_name',
            'profile_image',
            'last_seen',
            'is_online',
            'is_bot',
        ]
        fields = [
            'id',
            'first_name',
            'last_name',
            'bio',
            'username',
            'is_staff',
            'is_scam',
        ] + read_only_fields


class UserLastSeenSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
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
