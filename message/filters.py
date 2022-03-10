from django_filters.rest_framework import FilterSet

from .models import Message


class MessageFilter(FilterSet):
    class Meta:
        model = Message
        fields = {
            'content_type': ['iexact', 'in'],
            'sender_id': ['exact', 'in'],
            'sent_at': ['gte', 'lte', 'date', 'date__gte', 'date__lte'],
        }
