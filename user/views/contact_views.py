from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions


from user.querysets import get_user_contacts
from user.serializers import (ContactCreateSerializer,
                              UserInfoSerializer,
                              ContactUpdateSerializer)

User = get_user_model()


class ContactViewSet(viewsets.ModelViewSet):
    lookup_field = "contacted_user_id"
    lookup_url_kwarg = 'user_id'

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContactCreateSerializer

    def get_queryset(self):
        qs = get_user_contacts(self.request.user)
        if self.action in ['list', 'retrieve']:
            users = qs.values_list("contacted_user", flat=True)
            qs = User.objects.filter(id__in=users)
        return qs

    def get_object(self):
        if self.action == 'retrieve':
            self.lookup_field = 'id'
        return super().get_object()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return UserInfoSerializer
        if self.action in ['update', 'partial_update']:
            return ContactUpdateSerializer
        return super().get_serializer_class()
