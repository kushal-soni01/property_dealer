from rest_framework import serializers
from .models import Locality, LocalityProfile, Property, PropertyImage, PropertyHistory, Chat, ChatMessage
from django.contrib.auth.models import User

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


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'property', 'image', 'alt_text', 'is_primary', 'uploaded_at']


class PropertyHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = PropertyHistory
        fields = ['id', 'property', 'change_type', 'old_value', 'new_value', 'changed_by', 'changed_by_name', 'changed_at', 'description']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    sender_email = serializers.CharField(source='sender.email', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'chat', 'sender', 'sender_name', 'sender_email', 'message', 'created_at', 'is_read']


class ChatSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    admin_name = serializers.CharField(source='admin.username', read_only=True, allow_null=True)
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'user', 'user_name', 'property', 'property_title', 'admin', 'admin_name', 'created_at', 'updated_at', 'is_active', 'messages']