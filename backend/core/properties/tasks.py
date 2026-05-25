import os
import json
import requests
from celery import shared_task
from .models import Locality, LocalityProfile

@shared_task
def enrich_locality_pipeline(locality_id):
    debug_file = os.path.join(os.path.dirname(__file__), "task_debug.log")
    try:
        with open(debug_file, "a") as f:
            f.write(f"\n[TASK START] Processing locality_id={locality_id}\n")
        
        # Use get_or_none and proper exception handling
        from django.db import connections
        from django.core.exceptions import ObjectDoesNotExist
        
        try:
            locality = Locality.objects.select_related('profile').get(id=locality_id)
        except Locality.DoesNotExist:
            with open(debug_file, "a") as f:
                f.write(f"[ERROR] Locality with ID {locality_id} not found\n")
            return f"Locality {locality_id} not found"
        
        with open(debug_file, "a") as f:
            f.write(f"[INFO] Found locality: {locality.name}\n")
        
        serp_key = os.getenv("SERPAPI_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")
        
        if not serp_key or not groq_key:
            with open(debug_file, "a") as f:
                f.write(f"[ERROR] Missing API keys: SERPAPI={bool(serp_key)}, GROQ={bool(groq_key)}\n")
            return f"Missing API keys"

        # 1. Query SerpAPI for multiple POI categories like Google Maps
        with open(debug_file, "a") as f:
            f.write(f"[INFO] Querying SerpAPI for {locality.name} - Multiple categories\n")
            
        serp_url = "https://serpapi.com/search.json"
        
        # Query multiple place types
        place_queries = {
            "restaurants": "restaurants, cafes",
            "hospitals": "hospitals, clinics, medical centers",
            "tourist_attractions": "tourist attractions, landmarks, museums",
            "shopping": "shopping malls, shopping centers, retail",
            "schools": "schools, colleges, universities",
            "parks": "parks, recreation areas, gardens",
            "transit": "metro stations, bus stops, train stations"
        }
        
        nearby_places_data = {}
        
        for category, query in place_queries.items():
            try:
                params = {
                    "engine": "google_maps",
                    "q": query,
                    "ll": f"@{locality.latitude},{locality.longitude},14z",
                    "type": "search",
                    "api_key": serp_key
                }
                
                response = requests.get(serp_url, params=params, timeout=15)
                raw_data = response.json()
                
                cleaned_places = []
                for item in raw_data.get("local_results", [])[:5]:  # Top 5 for each category
                    cleaned_places.append({
                        "title": item.get("title"),
                        "type": item.get("type"),
                        "rating": item.get("rating"),
                        "reviews": item.get("reviews"),
                        "address": item.get("address"),
                        "distance": item.get("distance")
                    })
                
                nearby_places_data[category] = {
                    "count": len(cleaned_places),
                    "places": cleaned_places,
                    "avg_rating": round(sum([p.get("rating", 0) for p in cleaned_places]) / len(cleaned_places), 1) if cleaned_places else 0
                }
                
                with open(debug_file, "a") as f:
                    f.write(f"[INFO] {category}: {len(cleaned_places)} places found\n")
                    
            except Exception as e:
                with open(debug_file, "a") as f:
                    f.write(f"[WARN] Error querying {category}: {str(e)}\n")
                nearby_places_data[category] = {"count": 0, "places": [], "avg_rating": 0}
        
        # Combine all places for Groq analysis
        cleaned_places = []
        for category, data in nearby_places_data.items():
            cleaned_places.extend(data["places"])

        # 2. Query Groq API via standard REST endpoint
        with open(debug_file, "a") as f:
            f.write(f"[INFO] Querying Groq API\n")
            
        groq_url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }
        
        system_instructions = (
            "You are a professional real estate deployment AI analyst. "
            "Analyze the location data including nearby restaurants, hospitals, attractions, and infrastructure. "
            "Return strictly raw valid JSON. "
            "Do not include markdown tags like ```json or any trailing prose. "
            "Match this structure perfectly:\n"
            "{\n"
            '  "tourist_rating": 4,\n'
            '  "commercial_rating": 5,\n'
            '  "market_dist_km": 1.2,\n'
            '  "transit_dist_km": 0.8,\n'
            '  "infrastructure_analysis": {\n'
            '    "restaurant_quality": "Excellent - 15+ restaurants nearby",\n'
            '    "hospital_access": "Good - 2.3km to nearest hospital",\n'
            '    "tourist_attractions": "Strong - Multiple landmarks within 3km",\n'
            '    "highway_distance": "1.5km to nearest highway",\n'
            '    "education": "Good schools and colleges nearby",\n'
            '    "safety_assessment": "High foot traffic, commercial area, well-lit"\n'
            '  },\n'
            '  "best_use_suggestions": ["Boutique Cafe", "Co-working Hub", "Retail Outlet"],\n'
            '  "summary": "High traffic density area optimal for immediate high-end commercial scaling."\n'
            "}"
        )
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": f"Locality: {locality.name}, {locality.city}. Surrounding Places: {json.dumps(cleaned_places)}"}
            ],
            "temperature": 0.1
        }
        
        groq_res = requests.post(groq_url, json=payload, headers=headers, timeout=20)
        with open(debug_file, "a") as f:
            f.write(f"[INFO] Groq response status: {groq_res.status_code}\n")
            f.write(f"[INFO] Groq response text: {groq_res.text}\n")
        
        try:
            groq_json = groq_res.json()
            with open(debug_file, "a") as f:
                f.write(f"[INFO] Groq JSON parsed successfully\n")
        except Exception as json_err:
            with open(debug_file, "a") as f:
                f.write(f"[ERROR] Failed to parse Groq JSON: {json_err}\n")
            raise
        
        try:
            ai_raw_text = groq_json["choices"][0]["message"]["content"].strip()
            with open(debug_file, "a") as f:
                f.write(f"[INFO] Extracted AI text successfully\n")
        except KeyError as key_err:
            with open(debug_file, "a") as f:
                f.write(f"[ERROR] Key error accessing choices: {key_err}\n")
                f.write(f"[ERROR] Groq response keys: {groq_json.keys()}\n")
            raise
        
        # Strip code fences if the LLM outputted them anyway
        if ai_raw_text.startswith("```"):
            ai_raw_text = ai_raw_text.strip("`").replace("json", "", 1).strip()
            
        ai_data = json.loads(ai_raw_text)

        # 3. Store analytical structured dataset back to database
        LocalityProfile.objects.update_or_create(
            locality=locality,
            defaults={
                'tourist_rating': ai_data.get('tourist_rating', 3),
                'commercial_rating': ai_data.get('commercial_rating', 3),
                'market_dist_km': ai_data.get('market_dist_km', 0.0),
                'transit_dist_km': ai_data.get('transit_dist_km', 0.0),
                'best_use_suggestions': ai_data.get('best_use_suggestions', []),
                'summary': ai_data.get('summary', ''),
                'nearby_places': nearby_places_data,
                'infrastructure_data': ai_data.get('infrastructure_analysis', {})
            }
        )
        with open(debug_file, "a") as f:
            f.write(f"[SUCCESS] Pipeline executed for {locality.name}\n")
        print(f"Pipeline executed successfully for locality: {locality.name}")
    except Exception as err:
        import traceback
        with open(debug_file, "a") as f:
            f.write(f"[ERROR] {str(err)}\n")
            f.write(f"[TRACEBACK] {traceback.format_exc()}\n")
        print(f"Error executing asynchronous pipeline execution: {str(err)}")