from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import VerifyCodeViewSet
from user.apps import UserConfig
app_name = UserConfig.name

router = DefaultRouter()
router.register('verify-code', VerifyCodeViewSet, basename='verify-code')

urlpatterns = [
    path('', include(router.urls))
]
