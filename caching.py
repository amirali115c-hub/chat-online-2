# Caching Module
import time
from collections import OrderedDict

class Cache:
    def __init__(self, max_size=1000, default_ttl=300):
        self.cache = OrderedDict()
        self.timestamps = {}
        self.max_size = max_size
        self.default_ttl = default_ttl  # Time to live in seconds

    def get(self, key):
        """Get value from cache"""
        if key not in self.cache:
            return None

        # Check if expired
        if self.is_expired(key):
            self.delete(key)
            return None

        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]

    def set(self, key, value, ttl=None):
        """Set value in cache"""
        if ttl is None:
            ttl = self.default_ttl

        # Check size limit
        if len(self.cache) >= self.max_size and key not in self.cache:
            # Remove oldest item
            oldest = next(iter(self.cache))
            self.delete(oldest)

        self.cache[key] = value
        self.timestamps[key] = time.time() + ttl

    def delete(self, key):
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.timestamps:
            del self.timestamps[key]

    def is_expired(self, key):
        """Check if key is expired"""
        if key not in self.timestamps:
            return True
        return time.time() > self.timestamps[key]

    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.timestamps.clear()

    def cleanup(self):
        """Remove expired entries"""
        expired_keys = [k for k in self.cache.keys() if self.is_expired(k)]
        for key in expired_keys:
            self.delete(key)

    def get_stats(self):
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': getattr(self, 'hits', 0) / max(getattr(self, 'hits', 0) + getattr(self, 'misses', 1), 1)
        }

# Global cache instances for different purposes
user_cache = Cache(max_size=5000, default_ttl=300)  # 5 minutes
stats_cache = Cache(max_size=100, default_ttl=60)  # 1 minute
room_cache = Cache(max_size=1000, default_ttl=120)  # 2 minutes

def cache_user(user_id):
    """Cache user data"""
    user_cache.set(f'user:{user_id}', user_id)

def get_cached_user(user_id):
    """Get cached user"""
    return user_cache.get(f'user:{user_id}')

def invalidate_user(user_id):
    """Invalidate user cache"""
    user_cache.delete(f'user:{user_id}')

def cache_stats(stats):
    """Cache platform stats"""
    stats_cache.set('platform_stats', stats)

def get_cached_stats():
    """Get cached stats"""
    return stats_cache.get('platform_stats')
