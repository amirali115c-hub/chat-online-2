"""
ChatOnline Blueprints
"""
from .auth_bp import auth_bp
from .pages_bp import pages_bp
from .admin_bp import admin_bp

__all__ = ['auth_bp', 'pages_bp', 'admin_bp']
