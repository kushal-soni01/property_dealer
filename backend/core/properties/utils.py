"""
Rate limiting utility for SerpAPI calls
Tracks API calls per user/IP and enforces rate limits
"""

import os
from datetime import datetime, timedelta
from django.core.cache import cache
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class SerpAPIRateLimiter:
    """
    Rate limiter for SerpAPI autocomplete requests
    Uses Django cache to track requests
    
    Default: 30 requests per 1 hour per user/IP
    """
    
    # Configuration
    MAX_REQUESTS_PER_HOUR = 30
    WINDOW_SIZE = 3600  # 1 hour in seconds
    CACHE_KEY_PREFIX = "serpapi_autocomplete_"
    
    @classmethod
    def get_client_identifier(cls, request):
        """
        Get unique identifier for the client (user or IP)
        Priority: authenticated user > IP address
        """
        if request.user.is_authenticated:
            return f"user_{request.user.id}"
        
        # Get IP address, handling proxies
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        return f"ip_{ip}"
    
    @classmethod
    def is_allowed(cls, request):
        """
        Check if request is allowed based on rate limit
        Returns: (is_allowed: bool, remaining_requests: int)
        """
        client_id = cls.get_client_identifier(request)
        cache_key = f"{cls.CACHE_KEY_PREFIX}{client_id}"
        
        # Get current request count
        request_count = cache.get(cache_key, 0)
        
        if request_count >= cls.MAX_REQUESTS_PER_HOUR:
            return False, 0
        
        # Increment counter
        new_count = request_count + 1
        cache.set(cache_key, new_count, cls.WINDOW_SIZE)
        
        remaining = cls.MAX_REQUESTS_PER_HOUR - new_count
        return True, remaining
    
    @classmethod
    def reset_for_client(cls, request):
        """Reset rate limit counter for a client (for testing/admin)"""
        client_id = cls.get_client_identifier(request)
        cache_key = f"{cls.CACHE_KEY_PREFIX}{client_id}"
        cache.delete(cache_key)
        logger.info(f"Rate limit reset for {client_id}")


def rate_limit_check(request):
    """
    Helper function to check rate limit
    Can be used as middleware or in views
    
    Usage:
        is_allowed, remaining = rate_limit_check(request)
        if not is_allowed:
            return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
    """
    return SerpAPIRateLimiter.is_allowed(request)


def get_rate_limit_response(request):
    """
    Generate a JSON response for rate limit exceeded scenario
    """
    return JsonResponse({
        'error': 'Rate limit exceeded',
        'message': f'Maximum {SerpAPIRateLimiter.MAX_REQUESTS_PER_HOUR} requests per hour allowed',
        'retry_after': SerpAPIRateLimiter.WINDOW_SIZE
    }, status=429)
