from rest_framework import mixins, viewsets

from global_id.views.mixins import GUIDCRUDMixin
from ..models import FakeChat


class FakeChatViewSet(GUIDCRUDMixin,
                      viewsets.GenericViewSet):
    queryset = FakeChat.objects\
        .prefetch_related("_guid").all()
