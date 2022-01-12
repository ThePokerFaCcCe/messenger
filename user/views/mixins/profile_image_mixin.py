from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser


class UserProfileMixin:
    @action(['get', "post", 'delete'], detail=True,
            url_path=r'profile-image',
            parser_classes=[MultiPartParser])
    def profile_image(self, request, *args, **kwargs):
        if request.method == 'GET':
            return self.get_profile_image()
        if request.method == 'POST':
            return self.update_profile_image()
        if request.method == 'DELETE':
            return self.delete_profile_image()

    def get_profile_image(self):
        """Get user's `profile_image`"""
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update_profile_image(self):
        """Update user's `profile_image`"""
        user = self.get_object()
        user_old_profile = user.profile_image

        serializer = self.get_serializer(user,
                                         data=self.request.data)
        serializer.is_valid(raise_exception=True)

        if user_old_profile is None:
            status_code = status.HTTP_201_CREATED
        else:
            user_old_profile.delete()
            serializer.save()
            status_code = status.HTTP_200_OK

        return Response(serializer.data, status=status_code)

    def delete_profile_image(self):
        """Delete user's `profile_image`"""
        user = self.get_object()
        user.delete_profile_image()
        return Response(status=status.HTTP_204_NO_CONTENT)
