from django.db import models
from django.contrib.auth.models import User

class Locality(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    location = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Sector/Area/Landmark name (e.g., 'Sector 32', 'Downtown Area')"
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['latitude', 'longitude'],
                condition=models.Q(latitude__isnull=False, longitude__isnull=False),
                name='unique_coordinates'
            ),
        ]

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
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-uploaded_at']

    def __str__(self):
        return f"Image for {self.property.title}"


class PropertyHistory(models.Model):
    CHANGE_TYPES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('price_changed', 'Price Changed'),
        ('status_changed', 'Status Changed'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='history')
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.property.title} - {self.change_type}"


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='chats')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat: {self.user.username} - {self.property.title}"


class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username}"