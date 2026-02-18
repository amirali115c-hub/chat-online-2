# Rate Limiting Module
import time
from collections import defaultdict
from flask import request, jsonify
from functools import wraps

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.messages = defaultdict(list)
        self.logins = defaultdict(list)

    def check_rate_limit(self, key, action='request', limits=None):
        """Check if key has exceeded rate limit"""
        if limits is None:
            limits = {
                'request': {'max': 30, 'window': 60},      # 30 requests per minute
                'message': {'max': 20, 'window': 60},     # 20 messages per minute
                'login': {'max': 5, 'window': 300},       # 5 login attempts per 5 minutes
                'register': {'max': 3, 'window': 600},     # 3 registrations per 10 minutes
            }

        current_time = time.time()
        limit_config = limits.get(action, {'max': 30, 'window': 60})

        if action == 'request':
            store = self.requests
        elif action == 'message':
            store = self.messages
        else:
            store = self.logins

        # Clean old entries
        store[key] = [t for t in store[key] if current_time - t < limit_config['window']]

        if len(store[key]) >= limit_config['max']:
            return False, limit_config['window']

        store[key].append(current_time)
        return True, 0

    def reset(self, key):
        """Reset rate limit for a key"""
        if key in self.requests:
            del self.requests[key]
        if key in self.messages:
            del self.messages[key]
        if key in self.logins:
            del self.logins[key]

# Global rate limiter instance
rate_limiter = RateLimiter()

def get_client_ip():
    """Get client IP address"""
    # Check common proxy headers
    for header in ['X-Forwarded-For', 'X-Real-IP', 'CF-Connecting-IP']:
        if request.headers.get(header):
            return request.headers.get(header).split(',')[0].strip()
    return request.remote_addr

def rate_limit(action='request'):
    """Decorator for rate limiting"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            client_ip = get_client_ip()
            allowed, retry_after = rate_limiter.check_rate_limit(client_ip, action)

            if not allowed:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'RATE_LIMITED',
                        'message': f'Too many requests. Please try again later.',
                        'retry_after': retry_after
                    }
                }), 429

            return f(*args, **kwargs)
        return wrapped
    return decorator

# IP Blacklist
ip_blacklist = set()
temporary_bans = {}  # {ip: unban_time}

def ban_ip(ip, duration_seconds=3600):
    """Ban an IP temporarily"""
    temporary_bans[ip] = time.time() + duration_seconds
    ip_blacklist.add(ip)

def unban_ip(ip):
    """Unban an IP"""
    if ip in ip_blacklist:
        ip_blacklist.remove(ip)
    if ip in temporary_bans:
        del temporary_bans[ip]

def is_ip_banned(ip):
    """Check if IP is banned"""
    if ip in ip_blacklist:
        if ip in temporary_bans:
            if time.time() > temporary_bans[ip]:
                unban_ip(ip)
                return False
        return True
    return False

def cleanup_expired_bans():
    """Clean up expired temporary bans"""
    current_time = time.time()
    expired = [ip for ip, unban_time in temporary_bans.items() if current_time > unban_time]
    for ip in expired:
        unban_ip(ip)
