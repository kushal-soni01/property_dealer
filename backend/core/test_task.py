import django
import os
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from properties.models import Locality, LocalityProfile
from properties.tasks import enrich_locality_pipeline

# Create or get a test locality
loc, created = Locality.objects.get_or_create(
    name="Test Market",
    latitude=28.5355,
    longitude=77.3910,
    defaults={'city': 'New Delhi'}
)

print(f"\n✓ Locality: {loc.name} (ID: {loc.id}) - Created: {created}")
try:
    print(f"  Has Profile: {loc.profile is not None}")
except:
    print(f"  Has Profile: False")

# Queue the task
print(f"\n→ Queueing enrichment task...")
task_id = enrich_locality_pipeline.delay(loc.id)
print(f"✓ Task queued: {task_id}")

# Wait for task to complete (Celery worker should process it)
print(f"\n⏳ Waiting 5 seconds for Celery worker to process...")
time.sleep(5)

# Refresh locality from database
loc.refresh_from_db()
print(f"✓ Locality refreshed from database")

# Check if profile exists now
try:
    profile = loc.profile
    print(f"\n✓✓✓ AI PROFILE CREATED! ✓✓✓")
    print(f"  Tourist Rating: {profile.tourist_rating}")
    print(f"  Commercial Rating: {profile.commercial_rating}")
    print(f"  Summary: {profile.summary[:100]}...")
    print(f"  Infrastructure: {list(profile.infrastructure_data.keys())}")
    print(f"  Nearby Places Categories: {list(profile.nearby_places.keys())}")
except Exception as e:
    print(f"\n✗ Profile not created yet: {e}")
    
# Check debug log
debug_file = "task_debug.log"
if os.path.exists(debug_file):
    with open(debug_file, "r") as f:
        content = f.read()
        print(f"\n📄 Last 300 chars of Debug Log:")
        print(content[-300:] if len(content) > 300 else content)
else:
    print(f"\n✗ Debug log not found at: {debug_file}")

