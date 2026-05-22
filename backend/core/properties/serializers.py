from rest_framework import serializers
from .models import Locality, LocalityProfile, Property

class LocalityProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalityProfile
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Fallback if field is string instead of a true JSON array
        if isinstance(ret.get('best_use_suggestions'), str):
            import json
            try:
                ret['best_use_suggestions'] = json.loads(ret['best_use_suggestions'])
            except:
                ret['best_use_suggestions'] = []
        return ret

class LocalitySerializer(serializers.ModelSerializer):
    profile = LocalityProfileSerializer(read_only=True)

    class Meta:
        model = Locality
        fields = ['id', 'name', 'city', 'latitude', 'longitude', 'profile']

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'