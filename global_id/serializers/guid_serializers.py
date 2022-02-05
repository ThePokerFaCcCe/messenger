from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework import serializers
from generic_relations.relations import GenericRelatedField

from global_id.models import GUID

model_serializers = settings.GLOBAL_ID_CHAT_SERIALIZERS

chat_serializers = {
    import_string(model): import_string(serializer)()
    for model, serializer in model_serializers.items()
}


class GUIDSerializer(serializers.ModelSerializer):
    chat = GenericRelatedField(chat_serializers)

    class Meta:
        model = GUID
        fields = [
            'guid',
            'chat',
        ]


class GUIDTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = GUID
        fields = [
            'guid',
        ]
