from rest_framework import viewsets, permissions, response, status
from rest_framework.decorators import action

from community.serializers import JoinCommunitySerializer


class CommunityJoinMixin(viewsets.GenericViewSet):

    def get_permissions(self):
        if self.action == 'join':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'join':
            return JoinCommunitySerializer
        return super().get_serializer_class()

    @action(['post'], detail=False)
    def join(self, request, *args, **kwargs):
        """Join to community"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
