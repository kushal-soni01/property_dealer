from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from properties.views import LocalityViewSet, PropertyViewSet

router = DefaultRouter()
router.register(r'localities', LocalityViewSet)
router.register(r'properties', PropertyViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]