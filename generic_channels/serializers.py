from rest_framework import serializers


class ConsumerContentSerializer(serializers.Serializer):
    action = serializers.RegexField(
        r'^[a-z]+[_.]?[a-z]+$',
        error_messages={
            "invalid": 'Only [a-z] chars and one of ["." or "_"] are allowed'
        })
    body = serializers.DictField(required=False)
