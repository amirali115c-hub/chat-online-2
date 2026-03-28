"""
Configuration loader — chatonline
All sensitive values MUST come from environment variables.
Defaults are DEV-ONLY and will refuse to run in production.
"""

import os
import secrets
from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str, default: str = None, secret: bool = False) -> str:
    """Get env var; fail loudly if required but missing."""
    val = os.environ.get(name, default)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    if secret and (val.startswith("chat-online") or val == "admin" or len(val) < 32):
        raise RuntimeError(
            f"INSECURE: {name} is using a weak default value. "
            f"Set a strong value in your environment."
        )
    return val


def _gen_secret() -> str:
    """Generate a cryptographically strong random secret."""
    return secrets.token_hex(64)


class Config:
    """Base configuration — production-ready defaults."""

    # Flask
    # SECURITY: Must be set via SECRET_KEY env var in production.
    # Auto-generates only for local dev convenience (not cryptographically validated).
    _dev_secret = os.environ.get("SECRET_KEY", None)
    SECRET_KEY = _dev_secret or _gen_secret()

    # JWT — must be set in production
    _dev_jwt = os.environ.get("JWT_SECRET", None)
    JWT_SECRET = _dev_jwt or (os.environ.get("FLASK_ENV") != "production" and _gen_secret()) or ""
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET must be set in production (non-development) environments.")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24

    # Database
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///chat_online.db")
    USE_POSTGRES = "postgresql" in DATABASE_URL.lower()

    if not USE_POSTGRES:
        db_path = DATABASE_URL.replace("sqlite:///", "").lstrip("/")
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL", "")

    # Mail
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")

    # Security — production-safe cookie settings
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    SESSION_COOKIE_HTTPONLY = os.environ.get("SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")

    # Rate Limiting
    RATELIMIT_DEFAULT = os.environ.get("RATELIMIT_DEFAULT", "200 per day")
    RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "")

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = os.environ.get("LOG_FILE", "logs/chat-online.log")

    # Socket.IO
    SOCKETIO_ASYNC_MODE = os.environ.get("SOCKETIO_ASYNC_MODE", "threading")
    # SECURITY: CORS defaults to same-origin in production; allow list in dev via env var
    SOCKETIO_CORS_ORIGINS = os.environ.get(
        "SOCKETIO_CORS_ORIGINS",
        "*" if os.environ.get("FLASK_ENV") == "development" else ""
    )

    # Admin — no defaults; MUST be set via env vars
    @property
    def ADMIN_USERNAME(self):
        val = os.environ.get("ADMIN_USERNAME", "")
        if not val:
            raise RuntimeError("ADMIN_USERNAME environment variable is required.")
        return val

    @property
    def ADMIN_PASSWORD(self):
        val = os.environ.get("ADMIN_PASSWORD", "")
        if not val or len(val) < 10:
            raise RuntimeError(
                "ADMIN_PASSWORD must be at least 10 characters. "
                "Set a strong password via the ADMIN_PASSWORD environment variable."
            )
        return val

    # File uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = "static/uploads"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # Moderation
    MODERATION_ENABLED = os.environ.get("MODERATION_ENABLED", "true").lower() == "true"

    # Verification code expiry (minutes)
    VERIFICATION_CODE_EXPIRY = int(os.environ.get("VERIFICATION_CODE_EXPIRY", "10"))
    PASSWORD_RESET_EXPIRY = int(os.environ.get("PASSWORD_RESET_EXPIRY", "30"))


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    def __init__(self):
        # Verify all required production secrets are strong
        import os

        if not os.environ.get("ADMIN_USERNAME"):
            raise RuntimeError("ADMIN_USERNAME is required in production.")
        if not os.environ.get("ADMIN_PASSWORD") or len(os.environ.get("ADMIN_PASSWORD", "")) < 10:
            raise RuntimeError("ADMIN_PASSWORD must be at least 10 characters in production.")
        if not os.environ.get("JWT_SECRET") or len(os.environ.get("JWT_SECRET", "")) < 32:
            raise RuntimeError("JWT_SECRET must be set and at least 32 characters in production.")
        if not os.environ.get("SECRET_KEY") or len(os.environ.get("SECRET_KEY", "")) < 32:
            raise RuntimeError("SECRET_KEY must be set and at least 32 characters in production.")


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    DATABASE_URL = "sqlite:///test_chat_online.db"
    SESSION_COOKIE_SECURE = False
    SOCKETIO_CORS_ORIGINS = "*"


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)()
