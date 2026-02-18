import secrets
import functools
from flask import session, request, jsonify, render_template

# CSRF token configuration
CSRF_TOKEN_NAME = 'csrf_token'
CSRF_TOKEN_LENGTH = 32

def generate_csrf_token():
    """Generate a CSRF token for the session"""
    if CSRF_TOKEN_NAME not in session:
        session[CSRF_TOKEN_NAME] = secrets.token_hex(CSRF_TOKEN_LENGTH)
    return session[CSRF_TOKEN_NAME]

def validate_csrf_token(token):
    """Validate CSRF token"""
    session_token = session.get(CSRF_TOKEN_NAME)
    if not session_token or not token:
        return False
    # Use timing-safe comparison
    return secrets.compare_digest(session_token, token)

def csrf_required(f):
    """Decorator to require CSRF token for POST/PUT/DELETE requests"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip CSRF for API requests that use JWT auth
        if request.path.startswith('/api/'):
            # Check if there's a valid auth token
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                return f(*args, **kwargs)

        # For form submissions, validate CSRF token
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            if not validate_csrf_token(token):
                return jsonify({
                    'success': False,
                    'error': {'code': 'CSRF_ERROR', 'message': 'Invalid CSRF token. Please refresh the page and try again.'}
                }), 403
        return f(*args, **kwargs)
    return decorated_function
