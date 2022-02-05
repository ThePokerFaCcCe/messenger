import django
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType

from global_id.serializers import GUIDTextSerializer


class GUIDCRUDMixin:
    _guid_generic_field = '_guid'

    def get_serializer_class(self):
        if self.action == 'guid':
            return GUIDTextSerializer
        return super().get_serializer_class()

    @action(['get', 'post'], detail=True)
    def guid(self, r, *args, **kwargs):
        obj = self.get_object()
        guid = getattr(obj, self._guid_generic_field).first()
        if r.method == 'GET':
            serializer = self.get_serializer(guid)
        elif r.method == 'POST':
            serializer = self.get_serializer(
                guid, data=r.data)
            serializer.is_valid(raise_exception=True)
            data = {
                'chat_content_type':
                ContentType.objects.get_for_model(obj),
                'chat_id': obj.pk
            } if not guid else {}
            serializer.save(**data)
        return Response(serializer.data)

    @guid.mapping.delete
    def delete_guid(self, *args, **kwargs):
        obj = self.get_object()
        getattr(obj, self._guid_generic_field).all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
