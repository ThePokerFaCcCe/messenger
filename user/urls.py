from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.routers import NestedNoLookupRouter
from user.views import (DeviceViewSet, UserViewSet,
                        SelfUserViewSet, ContactViewSet)
from user.apps import UserConfig

app_name = UserConfig.name

router = DefaultRouter()
router.register('device', DeviceViewSet, basename='device')
router.register('user', UserViewSet, basename='user')
router.register('contact', ContactViewSet, basename='contact')

nl_user_router = NestedNoLookupRouter(router, 'user')
nl_user_router.register('me', SelfUserViewSet, basename='user-me')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(nl_user_router.urls)),
]
