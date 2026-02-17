# Website Health & Analytics Module
# Add this to your app.py

# ==================== HEALTH MONITORING ====================

import gc
import psutil
import logging
from collections import deque
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Health monitoring storage
health_data = {
    'page_load_times': deque(maxlen=100),  # Track recent page load times
    'errors': deque(maxlen=100),  # Track recent errors
    'page_views': deque(maxlen=1000),  # Track page views
    '404_pages': deque(maxlen=50),  # Track 404 pages
    'login_failures': deque(maxlen=50),  # Track failed logins
    'suspicious_activity': deque(maxlen=100),  # Track suspicious activity
    'startup_time': datetime.now(),
    'checks': {}
}

def check_database():
    """Check database connectivity"""
    try:
        start = time.time()
        db = get_db()
        db.execute('SELECT 1')
        elapsed = (time.time() - start) * 1000
        return {'status': 'healthy', 'response_time_ms': round(elapsed, 2)}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def check_disk_space():
    """Check disk space"""
    try:
        usage = psutil.disk_usage('/')
        return {
            'status': 'healthy' if usage.percent < 90 else 'warning',
            'total_gb': round(usage.total / (1024**3), 2),
            'used_gb': round(usage.used / (1024**3), 2),
            'free_gb': round(usage.free / (1024**3), 2),
            'percent_used': usage.percent
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def check_memory():
    """Check memory usage"""
    try:
        mem = psutil.virtual_memory()
        return {
            'status': 'healthy' if mem.percent < 90 else 'warning',
            'total_gb': round(mem.total / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'percent_used': mem.percent
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def check_socket_connections():
    """Check Socket.IO connections"""
    try:
        total = len(active_connections)
        return {
            'status': 'healthy',
            'total_connections': total,
            'guests': sum(1 for c in active_connections.values() if c.get('is_guest')),
            'registered': total - sum(1 for c in active_connections.values() if c.get('is_guest'))
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def check_uptime():
    """Check server uptime"""
    try:
        uptime = datetime.now() - health_data['startup_time']
        return {
            'status': 'healthy',
            'uptime_seconds': uptime.total_seconds(),
            'uptime_hours': uptime.total_seconds() / 3600,
            'startup_time': health_data['startup_time'].isoformat()
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def run_health_check():
    """Run all health checks"""
    health_data['checks'] = {
        'database': check_database(),
        'disk': check_disk_space(),
        'memory': check_memory(),
        'socket': check_socket_connections(),
        'uptime': check_uptime()
    }
    
    # Determine overall status
    statuses = [c.get('status') for c in health_data['checks'].values()]
    
    if 'error' in statuses:
        overall = 'critical'
    elif 'warning' in statuses:
        overall = 'warning'
    else:
        overall = 'healthy'
    
    health_data['checks']['overall'] = {
        'status': overall,
        'timestamp': datetime.now().isoformat()
    }
    
    return health_data['checks']

def log_error(error_type, message, path='', details=None):
    """Log an error for tracking"""
    error = {
        'type': error_type,
        'message': message,
        'path': path,
        'details': details,
        'timestamp': datetime.now().isoformat(),
        'ip': get_client_ip() if 'get_client_ip' in dir() else None
    }
    health_data['errors'].append(error)
    logger.error(f"[{error_type}] {message} - {path}")
    return error

def log_page_view(page, user_type='guest'):
    """Log a page view"""
    view = {
        'page': page,
        'user_type': user_type,
        'timestamp': datetime.now().isoformat(),
        'ip': get_client_ip() if 'get_client_ip' in dir() else None
    }
    health_data['page_views'].append(view)

def log_404(page):
    """Log a 404 page"""
    error = {
        'page': page,
        'timestamp': datetime.now().isoformat(),
        'ip': get_client_ip() if 'get_client_ip' in dir() else None
    }
    health_data['404_pages'].append(error)

def get_analytics(days=7):
    """Get analytics data"""
    cutoff = datetime.now() - timedelta(days=days)
    views = [v for v in health_data['page_views'] if datetime.fromisoformat(v['timestamp']) > cutoff]
    
    # Count page views
    page_counts = {}
    for view in views:
        page = view['page']
        page_counts[page] = page_counts.get(page, 0) + 1
    
    # Sort by views
    popular_pages = sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    
    return {
        'period_days': days,
        'total_views': len(views),
        'unique_pages': len(page_counts),
        'popular_pages': [{'page': p[0], 'views': p[1]} for p in popular_pages],
        'errors_count': len([e for e in health_data['errors'] if datetime.fromisoformat(e['timestamp']) > cutoff]),
        '404_count': len([e for e in health_data['404_pages'] if datetime.fromisoformat(e['timestamp']) > cutoff])
    }

def get_health_report():
    """Generate comprehensive health report"""
    checks = run_health_check()
    analytics = get_analytics(1)  # Last 24 hours
    
    # Find issues
    issues = []
    
    # Check for warnings in health
    for check_name, check_data in checks.items():
        if check_name == 'overall':
            continue
        if check_data.get('status') == 'warning':
            issues.append({
                'type': 'warning',
                'source': check_name,
                'message': f"{check_name} has warnings",
                'details': check_data
            })
    
    # Check for errors
    recent_errors = [e for e in health_data['errors'] 
                     if datetime.fromisoformat(e['timestamp']) > datetime.now() - timedelta(hours=1)]
    for error in recent_errors:
        issues.append({
            'type': 'error',
            'source': error['type'],
            'message': error['message'],
            'path': error.get('path', '')
        })
    
    # Check for 404s
    recent_404s = [e for e in health_data['404_pages'] 
                    if datetime.fromisoformat(e['timestamp']) > datetime.now() - timedelta(hours=1)]
    for error in recent_404s:
        issues.append({
            'type': '404',
            'source': 'broken_link',
            'message': f"404: {error['page']}",
            'path': error['page']
        })
    
    return {
        'timestamp': datetime.now().isoformat(),
        'health': checks,
        'analytics': analytics,
        'issues': issues,
        'issue_count': len(issues)
    }
