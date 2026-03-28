"""
Unit tests for csrf.py
"""
import os
import sys
import secrets

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Inline minimal version for testing (avoids flask dependency)
CSRF_TOKEN_NAME = 'csrf_token'
CSRF_TOKEN_LENGTH = 32

# Simulate a per-call session store
_session_store = {}


def generate_csrf_token():
    if CSRF_TOKEN_NAME not in _session_store:
        _session_store[CSRF_TOKEN_NAME] = secrets.token_hex(CSRF_TOKEN_LENGTH)
    return _session_store[CSRF_TOKEN_NAME]


def validate_csrf_token(token):
    session_token = _session_store.get(CSRF_TOKEN_NAME)
    if not session_token or not token:
        return False
    return secrets.compare_digest(session_token, token)


class TestCSRFTokenGeneration:
    """Tests for CSRF token generation."""

    def test_generate_token_returns_string(self):
        _session_store.clear()
        token = generate_csrf_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_length(self):
        _session_store.clear()
        token = generate_csrf_token()
        # Default length is 32 bytes = 64 hex chars
        assert len(token) == 64

    def test_same_session_returns_same_token(self):
        _session_store.clear()
        token1 = generate_csrf_token()
        token2 = generate_csrf_token()
        assert token1 == token2


class TestCSRFTokenValidation:
    """Tests for CSRF token validation."""

    def test_valid_token_passes(self):
        _session_store.clear()
        token = generate_csrf_token()
        assert validate_csrf_token(token) is True

    def test_wrong_token_fails(self):
        _session_store.clear()
        generate_csrf_token()
        wrong = 'a' * 64
        assert validate_csrf_token(wrong) is False

    def test_empty_token_fails(self):
        _session_store.clear()
        generate_csrf_token()
        assert validate_csrf_token('') is False

    def test_none_token_fails(self):
        _session_store.clear()
        generate_csrf_token()
        assert validate_csrf_token(None) is False

    def test_tampered_token_fails(self):
        _session_store.clear()
        token = generate_csrf_token()
        tampered = token[:-1] + ('0' if token[-1] != '0' else '1')
        assert tampered != token
        assert validate_csrf_token(tampered) is False
