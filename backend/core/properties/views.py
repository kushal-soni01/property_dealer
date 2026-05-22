from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
import threading
import logging
from .models import Locality, Property
from .serializers import LocalitySerializer, PropertySerializer
from .tasks import enrich_locality_pipeline

logger = logging.getLogger(__name__)

class LocalityViewSet(viewsets.ModelViewSet):
    queryset = Locality.objects.all().select_related('profile')
    serializer_class = LocalitySerializer

    def create(self, request, *args, **kwargs):
        lat = request.data.get('latitude')
        lng = request.data.get('longitude')
        name = request.data.get('name')
        city = request.data.get('city')

        if not lat or not lng or not name or not city:
            return Response({"error": "Missing mandatory field records."}, status=status.HTTP_400_BAD_REQUEST)

        locality, created = Locality.objects.get_or_create(
            latitude=lat,
            longitude=lng,
            defaults={'name': name, 'city': city}
        )

        if created:
            print(f"✓ New locality created: {locality.id} ({name}, {city})")
            debug_file = "d:\\Broker\\backend\\core\\views_debug.log"
            with open(debug_file, "a") as f:
                f.write(f"\n[VIEW] Created locality {locality.id}\n")
            # Try async first, then fall back to background thread
            try:
                print(f"→ Attempting to queue Celery task for locality {locality.id}")
                with open(debug_file, "a") as f:
                    f.write(f"[VIEW] Calling enrich_locality_pipeline.delay({locality.id})\n")
                task_id = enrich_locality_pipeline.delay(locality.id)
                print(f"✓ Task queued successfully with ID: {task_id}")
                with open(debug_file, "a") as f:
                    f.write(f"[VIEW] Task queued: {task_id}\n")
            except Exception as e:
                print(f"✗ Celery task failed: {str(e)}, falling back to background thread")
                with open(debug_file, "a") as f:
                    f.write(f"[VIEW] Celery failed: {str(e)}\n")
                # Run in background thread so HTTP response isn't blocked
                thread = threading.Thread(target=enrich_locality_pipeline, args=(locality.id,), daemon=True)
                thread.start()
                print(f"✓ Background thread started for locality {locality.id}")
                with open(debug_file, "a") as f:
                    f.write(f"[VIEW] Background thread started\n")

        serializer = self.get_serializer(locality)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def properties(self, request, pk=None):
        locality = self.get_object()
        properties = Property.objects.filter(locality=locality)
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data)

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer