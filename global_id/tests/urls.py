from django.urls import include, path
from rest_framework import routers

from .apps import GlobalIdTestConfig
from .views import FakeChatViewSet

app_name = GlobalIdTestConfig.name

router = routers.DefaultRouter()
router.register('fakechat', FakeChatViewSet, basename='fake-chat')

urlpatterns = [
    path('', include(router.urls))
]
