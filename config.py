import os

class Config:
    # Security - Use environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chat-secret-key-change-in-production'
    DEBUG = False  # Set to False for production

    # Chat settings
    CHAT_TIMEOUT = 1800  # 30 minutes max chat session
    MAX_MESSAGE_LENGTH = 2000

    # Queue settings
    QUEUE_POLL_INTERVAL = 1  # seconds

    # Session settings - Secure for production
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'

    # Production settings
    if not DEBUG:
        SESSION_COOKIE_SECURE = True
        # Force HTTPS by redirecting HTTP to HTTPS
        # Add this to your web server (nginx/cloudflare)

    # Countries dictionary
    COUNTRIES = {
        "US": "United States",
        "GB": "United Kingdom",
        "CA": "Canada",
        "AU": "Australia",
        "IN": "India",
        "DE": "Germany",
        "FR": "France",
        "ES": "Spain",
        "IT": "Italy",
        "BR": "Brazil",
        "MX": "Mexico",
        "JP": "Japan",
        "KR": "South Korea",
        "CN": "China",
        "RU": "Russia",
        "NL": "Netherlands",
        "BE": "Belgium",
        "SE": "Sweden",
        "NO": "Norway",
        "DK": "Denmark",
        "FI": "Finland",
        "PL": "Poland",
        "PT": "Portugal",
        "IE": "Ireland",
        "NZ": "New Zealand",
        "SG": "Singapore",
        "MY": "Malaysia",
        "PH": "Philippines",
        "ID": "Indonesia",
        "TH": "Thailand",
        "VN": "Vietnam",
        "PK": "Pakistan",
        "BD": "Bangladesh",
        "EG": "Egypt",
        "ZA": "South Africa",
        "NG": "Nigeria",
        "KE": "Kenya",
        "AR": "Argentina",
        "CL": "Chile",
        "CO": "Colombia",
        "PE": "Peru",
        "VE": "Venezuela"
    }
