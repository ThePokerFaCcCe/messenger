from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import VerifyCodeViewSet, DeviceViewSet
from user.apps import UserConfig
app_name = UserConfig.name

router = DefaultRouter()
router.register('verify-code', VerifyCodeViewSet, basename='verify-code')
router.register('device', DeviceViewSet, basename='device')

urlpatterns = [
    path('', include(router.urls))
]
