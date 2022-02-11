from django.urls import path, include
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework.routers import DefaultRouter
from core.routers import NestedJustFirstLookupRouter

from community.views import (CommunityChatViewSet, InviteLinkNestedViewSet,
                             MemberNestedViewSet, RulesNestedViewSet)

basename = 'community-'

router = DefaultRouter()
router.register('', CommunityChatViewSet, basename='commnuity')

n_router = NestedDefaultRouter(router, '', lookup='community')
n_router.register('invite-link', InviteLinkNestedViewSet, basename=basename+'invite-link')
n_router.register('member', MemberNestedViewSet, basename=basename+'member')

nl_router = NestedJustFirstLookupRouter(router, '', lookup='community')
nl_router.register('rules', RulesNestedViewSet, basename=basename+'rules')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(n_router.urls)),
    path('', include(nl_router.urls)),
]
