from django.urls import path, include
from rest_framework.routers import DefaultRouter

from conversation.views import ConversationViewSet
from conversation.apps import ConversationConfig

app_name = ConversationConfig.name

router = DefaultRouter()
router.register('', ConversationViewSet, basename='conversation')

urlpatterns = [
    path("", include(router.urls))
]
