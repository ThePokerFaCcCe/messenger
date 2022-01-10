from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import (DeviceViewSet, UserViewSet)
from user.apps import UserConfig
app_name = UserConfig.name

router = DefaultRouter()
router.register('device', DeviceViewSet, basename='device')
router.register('', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls))
]
