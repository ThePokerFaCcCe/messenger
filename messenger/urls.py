import sys
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/v1/', include("user.urls")),
    path('api/v1/auth/', include("auth_app.urls")),
    path('api/v1/conversation/', include("conversation.urls")),
    path('api/v1/guid/', include("global_id.urls")),
]\
    + [  # Docs & Schema
        path("api/v1/schema/", SpectacularAPIView.as_view(), name='schema'),
        path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name='schema')),
]\
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

if 'test' in sys.argv:
    urlpatterns += [
        path('', include('global_id.tests.urls'))
    ]
