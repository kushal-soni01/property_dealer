from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework.routers import DefaultRouter
from properties.views import LocalityViewSet, PropertyViewSet, autocomplete_location, get_coordinates

router = DefaultRouter()
router.register(r'localities', LocalityViewSet)
router.register(r'properties', PropertyViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/autocomplete-location/', autocomplete_location, name='autocomplete-location'),
    path('api/get-coordinates/', get_coordinates, name='get-coordinates'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += staticfiles_urlpatterns()