from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import threading
import logging
import json
import requests
import os
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


# ==================== AUTOCOMPLETE & COORDINATE VIEWS ====================

@require_http_methods(["GET"])
@csrf_exempt
def autocomplete_location(request):
    """
    Autocomplete endpoint for location search
    Uses SerpAPI to find locations matching the query and city
    
    Query Parameters:
    - q: Search query (sector name, landmark, etc.)
    - city: City filter (required)
    
    Returns JSON with matching locations and their coordinates
    """
    # Rate limiting disabled - removed as per request
    
    query = request.GET.get('q', '').strip()
    city = request.GET.get('city', '').strip()
    
    # Validation
    if not query or len(query) < 2:
        return JsonResponse({
            'results': [],
            'message': 'Query too short (minimum 2 characters)',
            'api_status': 'user_input'
        })
    
    if not city:
        return JsonResponse({
            'error': 'City parameter is required',
            'api_status': 'user_input'
        }, status=400)
    
    serp_key = os.getenv('SERPAPI_API_KEY')
    if not serp_key:
        return JsonResponse({
            'results': [],
            'error': 'API not configured',
            'api_status': 'api_down',
            'message': 'SerpAPI key not configured. Please manually enter coordinates.'
        }, status=503)
    
    try:
        # Search for locations using SerpAPI
        serp_url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_maps",
            "q": f"{query} {city}",
            "type": "search",
            "api_key": serp_key
        }
        
        response = requests.get(serp_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract location results - try multiple response formats from SerpAPI
        results = []
        
        # Try local_results first (most common)
        local_results = data.get('local_results', [])
        
        # If empty, try places results
        if not local_results:
            local_results = data.get('places', [])
        
        # If still empty, try knowledge_graph locations
        if not local_results and data.get('knowledge_graph'):
            kg = data.get('knowledge_graph', {})
            if kg.get('type') == 'Place':
                local_results = [kg]
        
        logger.info(f"SerpAPI response - local_results: {len(local_results)}, places: {len(data.get('places', []))}")
        
        # Parse results with flexible field mapping
        for item in local_results[:10]:  # Limit to 10 results
            # Handle different SerpAPI response formats
            name = item.get('title') or item.get('name') or item.get('place_name') or ''
            address = item.get('address') or item.get('formatted_address') or ''
            lat = item.get('latitude') or item.get('lat')
            lng = item.get('longitude') or item.get('lng')

            # Handle nested coordinate formats from SerpAPI
            if lat is None or lng is None:
                gps = item.get('gps_coordinates') or item.get('gps') or {}
                if isinstance(gps, dict):
                    lat = lat if lat is not None else gps.get('latitude') or gps.get('lat')
                    lng = lng if lng is not None else gps.get('longitude') or gps.get('lng')

            if lat is None or lng is None:
                geometry = item.get('geometry') or {}
                if isinstance(geometry, dict):
                    location = geometry.get('location') or {}
                    if isinstance(location, dict):
                        lat = lat if lat is not None else location.get('lat')
                        lng = lng if lng is not None else location.get('lng')
            place_id = item.get('place_id') or item.get('id') or ''
            
            # Convert to float if string
            try:
                if isinstance(lat, str):
                    lat = float(lat)
                if isinstance(lng, str):
                    lng = float(lng)
            except (ValueError, TypeError):
                lat = None
                lng = None
            
            result = {
                'id': place_id,
                'name': name,
                'address': address,
                'latitude': lat,
                'longitude': lng,
                'type': item.get('type', 'location')
            }
            
            # Only include results with valid data
            if name and lat is not None and lng is not None:
                results.append(result)
        
        logger.info(f"Autocomplete: query='{query}', city='{city}', final_results={len(results)}")
        
        return JsonResponse({
            'results': results,
            'api_status': 'success',
            'query': query,
            'city': city,
            'count': len(results)
        })
    
    except requests.exceptions.Timeout:
        logger.warning(f"SerpAPI timeout for query: {query}")
        return JsonResponse({
            'results': [],
            'error': 'Request timeout',
            'api_status': 'api_down',
            'message': 'Location search is taking too long. Please manually enter coordinates.'
        }, status=503)
    
    except requests.exceptions.RequestException as e:
        logger.error(f"SerpAPI error: {str(e)}")
        return JsonResponse({
            'results': [],
            'error': 'API error',
            'api_status': 'api_down',
            'message': 'Location service is temporarily unavailable. Please manually enter coordinates.'
        }, status=503)
    
    except Exception as e:
        logger.error(f"Unexpected error in autocomplete: {str(e)}")
        return JsonResponse({
            'results': [],
            'error': 'Unexpected error',
            'api_status': 'error',
            'message': 'An unexpected error occurred. Please manually enter coordinates.'
        }, status=500)


@require_http_methods(["GET"])
@csrf_exempt
def get_coordinates(request):
    """
    Get coordinates for a specific location
    Used when autocomplete result is selected
    
    Query Parameters:
    - location: Location name or address
    - city: City name (for context)
    
    Returns JSON with latitude and longitude
    """
    # Rate limiting disabled - removed as per request
    
    location = request.GET.get('location', '').strip()
    city = request.GET.get('city', '').strip()
    
    if not location or not city:
        return JsonResponse({
            'error': 'Location and city parameters required',
            'api_status': 'user_input'
        }, status=400)
    
    serp_key = os.getenv('SERPAPI_API_KEY')
    if not serp_key:
        return JsonResponse({
            'error': 'API not configured',
            'api_status': 'api_down'
        }, status=503)
    
    try:
        serp_url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_maps",
            "q": f"{location} {city}",
            "type": "search",
            "api_key": serp_key
        }
        
        response = requests.get(serp_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        local_results = data.get('local_results', [])
        
        if local_results:
            first_result = local_results[0]
            return JsonResponse({
                'latitude': first_result.get('latitude'),
                'longitude': first_result.get('longitude'),
                'name': first_result.get('title', ''),
                'address': first_result.get('address', ''),
                'api_status': 'success'
            })
        else:
            return JsonResponse({
                'error': 'Location not found',
                'api_status': 'not_found'
            }, status=404)
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching coordinates: {str(e)}")
        return JsonResponse({
            'error': 'API error',
            'api_status': 'api_down'
        }, status=503)
    
    except Exception as e:
        logger.error(f"Unexpected error in get_coordinates: {str(e)}")
        return JsonResponse({
            'error': 'Unexpected error',
            'api_status': 'error'
        }, status=500)