import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from properties.models import Locality, LocalityProfile
from properties.tasks import enrich_locality_pipeline

# Create test locality with unique coordinates
loc, created = Locality.objects.get_or_create(
    name="Sync Test Market",
    latitude=29.0000,
    longitude=77.5000,
    defaults={'city': 'New Delhi'}
)

print(f"\n✓ Created Locality: {loc.name} (ID: {loc.id})")

# Delete any existing profile
LocalityProfile.objects.filter(locality=loc).delete()
print(f"✓ Cleared old profile")

# Run task SYNCHRONOUSLY (not with delay)
print(f"\n→ Running task synchronously...")
try:
    enrich_locality_pipeline(loc.id)  # Direct call, not .delay()
    print(f"✓ Task executed synchronously")
except Exception as e:
    print(f"✗ Task error: {e}")
    import traceback
    traceback.print_exc()

# Refresh and check
loc.refresh_from_db()
try:
    profile = loc.profile
    print(f"\n✓✓✓ PROFILE CREATED! ✓✓✓")
    print(f"  Tourist Rating: {profile.tourist_rating}")
    print(f"  Commercial Rating: {profile.commercial_rating}")
    print(f"  Summary: {profile.summary[:100] if profile.summary else 'N/A'}...")
except Exception as e:
    print(f"\n✗ Profile still missing: {e}")
