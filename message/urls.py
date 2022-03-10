from django.urls import include, path, register_converter
from rest_framework.routers import DefaultRouter

from .views import MessageViewSet

router = DefaultRouter()
router.register('', MessageViewSet, basename='message')


class NegativeIntConverter:
    regex = '-?\d+'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%d' % value


register_converter(NegativeIntConverter, 'negint')

urlpatterns = [
    path("<negint:chat_id>/", include(router.urls))
]
