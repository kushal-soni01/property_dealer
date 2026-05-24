from django.contrib import admin
from django import forms
from .models import Locality, LocalityProfile, Property
from .tasks import enrich_locality_pipeline
from .widgets import LocationAutocompleteWidget


class LocalityAdminForm(forms.ModelForm):
    class Meta:
        model = Locality
        fields = '__all__'
        widgets = {
            'latitude': forms.NumberInput(attrs={
                'readonly': 'readonly',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'readonly': 'readonly',
                'step': 'any'
            }),
        }

@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    form = LocalityAdminForm
    list_display = ('id', 'name', 'city', 'location', 'latitude', 'longitude', 'has_profile', 'created_at')
    list_filter = ('city', 'created_at')
    search_fields = ('name', 'city', 'location')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'city')
        }),
        ('Location', {
            'fields': ('location',),
            'description': 'Start typing a sector name, landmark, or area. Suggestions will appear automatically based on the city.'
        }),
        ('Coordinates', {
            'fields': ('latitude', 'longitude'),
            'description': 'These are auto-filled when you select a location from the autocomplete dropdown. They are read-only here.',
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    actions = ['trigger_ai_analysis']
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form to use LocationAutocompleteWidget"""
        try:
            form = super().get_form(request, obj, **kwargs)
            # Use custom widget for location field if it exists
            if 'location' in form.base_fields:
                form.base_fields['location'].widget = LocationAutocompleteWidget(city_field_name='city')
            return form
        except Exception as e:
            # Fallback to regular form if widget fails
            import logging
            logging.error(f"Error setting LocationAutocompleteWidget: {e}")
            return super().get_form(request, obj, **kwargs)
    
    def has_profile(self, obj):
        """Display if locality has AI analysis profile"""
        return hasattr(obj, 'profile') and obj.profile is not None
    has_profile.boolean = True
    has_profile.short_description = 'AI Profile Generated'
    
    def trigger_ai_analysis(self, request, queryset):
        """Action to manually trigger AI pipeline for selected localities"""
        count = 0
        for locality in queryset:
            try:
                # Queue the Celery task
                enrich_locality_pipeline.delay(locality.id)
                count += 1
            except Exception as e:
                self.message_user(request, f'Error processing {locality.name}: {str(e)}', level='ERROR')
        
        self.message_user(request, f'AI analysis queued for {count} locality(ies). Check back in 30 seconds.')
    
    trigger_ai_analysis.short_description = "Trigger AI Analysis Pipeline"

@admin.register(LocalityProfile)
class LocalityProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'locality', 'tourist_rating', 'commercial_rating', 'summary_preview', 'last_updated')
    list_filter = ('tourist_rating', 'commercial_rating', 'last_updated')
    search_fields = ('locality__name', 'summary')
    readonly_fields = ('last_updated', 'locality', 'summary_display', 'nearby_places_display', 'infrastructure_display')
    fieldsets = (
        ('Locality Reference', {
            'fields': ('locality',)
        }),
        ('Ratings & Distances', {
            'fields': ('tourist_rating', 'commercial_rating', 'market_dist_km', 'transit_dist_km')
        }),
        ('Infrastructure Analysis', {
            'fields': ('infrastructure_display',),
            'classes': ('wide',)
        }),
        ('Nearby Places', {
            'fields': ('nearby_places_display',),
            'classes': ('wide',)
        }),
        ('AI Analysis', {
            'fields': ('summary_display', 'summary'),
            'classes': ('wide',)
        }),
        ('Recommendations', {
            'fields': ('best_use_suggestions',)
        }),
        ('Metadata', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )
    
    def summary_display(self, obj):
        return obj.summary[:200] + "..." if len(obj.summary) > 200 else obj.summary
    summary_display.short_description = "Summary Preview"
    
    def nearby_places_display(self, obj):
        """Format nearby places for display"""
        if not obj.nearby_places:
            return "No data"
        html = "<div style='font-size: 12px; line-height: 1.6;'>"
        for category, data in obj.nearby_places.items():
            html += f"<strong>{category.replace('_', ' ').title()}:</strong> {data.get('count', 0)} places "
            html += f"(Avg Rating: {data.get('avg_rating', 'N/A')})<br>"
        html += "</div>"
        return html
    nearby_places_display.allow_tags = True
    nearby_places_display.short_description = "Nearby Places Summary"
    
    def infrastructure_display(self, obj):
        """Format infrastructure analysis for display"""
        if not obj.infrastructure_data:
            return "Analyzing..."
        html = "<div style='font-size: 12px; line-height: 1.8;'>"
        for key, value in obj.infrastructure_data.items():
            label = key.replace('_', ' ').title()
            html += f"<strong>{label}:</strong> {value}<br>"
        html += "</div>"
        return html
    infrastructure_display.allow_tags = True
    infrastructure_display.short_description = "Infrastructure Analysis"
    fieldsets = (
        ('Locality Reference', {
            'fields': ('locality',),
            'description': 'Read-only: The locality this profile analyzes'
        }),
        ('Ratings', {
            'fields': ('tourist_rating', 'commercial_rating')
        }),
        ('Infrastructure', {
            'fields': ('market_dist_km', 'transit_dist_km')
        }),
        ('AI Analysis', {
            'fields': ('summary_display', 'best_use_suggestions')
        }),
        ('Metadata', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )
    
    def summary_display(self, obj):
        """Display summary in read-only format"""
        return obj.summary if obj.summary else "No summary available"
    summary_display.short_description = "Summary"
    
    def summary_preview(self, obj):
        """Show preview of summary in list view"""
        if obj.summary:
            preview = obj.summary[:75]
            return preview + '...' if len(obj.summary) > 75 else preview
        return '—'
    summary_preview.short_description = "Summary Preview"

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'locality', 'price_display', 'created_at')
    list_filter = ('locality__city', 'created_at', 'price')
    search_fields = ('title', 'description', 'locality__name')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Property Information', {
            'fields': ('title', 'description', 'price')
        }),
        ('Location', {
            'fields': ('locality',),
            'description': 'Select the locality where this property is located'
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        """Format price for display"""
        return f"${obj.price:,.2f}"
    price_display.short_description = "Price"