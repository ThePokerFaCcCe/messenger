from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import (VerifyCodeViewSet, DeviceViewSet,
                        AccessViewSet, UserViewSet)
from user.apps import UserConfig
app_name = UserConfig.name

router = DefaultRouter()
router.register('verify-code', VerifyCodeViewSet, basename='verify-code')
router.register('device', DeviceViewSet, basename='device')
router.register('access', AccessViewSet, basename='access')
router.register('user', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls))
]
