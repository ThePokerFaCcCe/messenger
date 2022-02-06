from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .apps import GlobalIdConfig
from global_id.views import GUIDViewset

app_name = GlobalIdConfig.name

router = DefaultRouter()
router.register('', GUIDViewset, 'guid')

urlpatterns = [
    path('', include(router.urls))
]
