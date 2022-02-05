from django.urls import path, include
from rest_framework.routers import DefaultRouter

from global_id.views import GUIDViewset

router = DefaultRouter()
router.register('', GUIDViewset, 'guid')

urlpatterns = [
    path('', include(router.urls))
]
