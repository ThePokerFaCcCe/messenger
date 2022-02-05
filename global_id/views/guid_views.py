from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin

from global_id.models import GUID
from global_id.serializers import GUIDSerializer


class GUIDViewset(RetrieveModelMixin, GenericViewSet):
    queryset = GUID.objects.prefetch_related('chat').all()
    serializer_class = GUIDSerializer
    lookup_field = 'guid'
