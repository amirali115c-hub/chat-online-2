# Caching Module
import time
from collections import OrderedDict

class Cache:
    def __init__(self, max_size=1000, default_ttl=300):
        self.cache = OrderedDict()
        self.expiry = {}
        self.max_size = max_size
        self.default_ttl = default_ttl  # Default TTL in seconds (5 minutes)

    def get(self, key):
        """Get value from cache"""
        if key not in self.cache:
            return None

        # Check if expired
        if key in self.expiry and time.time() > self.expiry[key]:
            del self.cache[key]
            del self.expiry[key]
            return None

        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]

    def set(self, key, value, ttl=None):
        """Set value in cache"""
        if ttl is None:
            ttl = self.default_ttl

        # Remove oldest if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest = next(iter(self.cache))
            del self.cache[oldest]
            if oldest in self.expiry:
                del self.expiry[oldest]

        self.cache[key] = value
        self.expiry[key] = time.time() + ttl
        self.cache.move_to_end(key)

    def delete(self, key):
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.expiry:
            del self.expiry[key]

    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.expiry.clear()

    def cleanup_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [k for k, exp_time in self.expiry.items() if current_time > exp_time]
        for key in expired_keys:
            del self.cache[key]
            del self.expiry[key]

    def get_stats(self):
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'expired_count': sum(1 for exp_time in self.expiry.values() if time.time() > exp_time)
        }

# Global cache instances
user_cache = Cache(max_size=500, default_ttl=300)  # 5 minutes for user data
room_cache = Cache(max_size=200, default_ttl=60)  # 1 minute for room data
stats_cache = Cache(max_size=10, default_ttl=30)   # 30 seconds for stats
search_cache = Cache(max_size=100, default_ttl=120)  # 2 minutes for search results

# Cache helper functions
def cache_user(user_id):
    """Cache user data"""
    from database import get_user_by_id
    user = get_user_by_id(user_id)
    if user:
        user_cache.set(f"user:{user_id}", user)
    return user

def get_cached_user(user_id):
    """Get cached user data"""
    cached = user_cache.get(f"user:{user_id}")
    if cached:
        return cached
    return cache_user(user_id)

def invalidate_user(user_id):
    """Invalidate user cache"""
    user_cache.delete(f"user:{user_id}")

def cache_stats():
    """Cache platform stats"""
    from database import get_stats
    stats = get_stats()
    stats_cache.set('platform_stats', stats)
    return stats

def get_cached_stats():
    """Get cached stats"""
    cached = stats_cache.get('platform_stats')
    if cached:
        return cached
    return cache_stats()

def cache_rooms():
    """Cache room list"""
    from database import get_rooms
    rooms = get_rooms()
    room_cache.set('all_rooms', rooms)
    return rooms

def get_cached_rooms():
    """Get cached rooms"""
    cached = room_cache.get('all_rooms')
    if cached:
        return cached
    return cache_rooms()

def invalidate_rooms():
    """Invalidate room cache"""
    room_cache.delete('all_rooms')

def cleanup_all_caches():
    """Clean up all caches"""
    user_cache.cleanup_expired()
    room_cache.cleanup_expired()
    stats_cache.cleanup_expired()
    search_cache.cleanup_expired()
