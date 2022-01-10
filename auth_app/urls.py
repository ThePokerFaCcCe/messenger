from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (VerifyCodeViewSet, AccessViewSet)
from .apps import AuthConfig

app_name = AuthConfig.name

router = DefaultRouter()
router.register('verify-code', VerifyCodeViewSet, basename='verify-code')
router.register('access', AccessViewSet, basename='access')

urlpatterns = [
    path('', include(router.urls))
]
