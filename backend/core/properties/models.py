from django.db import models

class Locality(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('latitude', 'longitude')

    def __str__(self):
        return f"{self.name}, {self.city}"

class LocalityProfile(models.Model):
    locality = models.OneToOneField(Locality, on_delete=models.CASCADE, related_name='profile')
    tourist_rating = models.IntegerField(null=True, blank=True)
    commercial_rating = models.IntegerField(null=True, blank=True)
    market_dist_km = models.FloatField(null=True, blank=True)
    transit_dist_km = models.FloatField(null=True, blank=True)
    best_use_suggestions = models.JSONField(default=list, blank=True)
    summary = models.TextField(blank=True)
    nearby_places = models.JSONField(default=dict, blank=True)  # Stores restaurants, hospitals, attractions, etc.
    infrastructure_data = models.JSONField(default=dict, blank=True)  # Highways, schools, parks distance
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.locality.name}"

class Property(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title