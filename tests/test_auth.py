"""
Unit tests for auth.py
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///test_chat_online.db'
os.environ['ADMIN_USERNAME'] = 'testadmin'
os.environ['ADMIN_PASSWORD'] = 'testpassword123'
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only-32chars'
os.environ['JWT_SECRET'] = 'test-jwt-secret-key-for-testing-only'

import database as db_module

db_module.DATABASE_URL = 'sqlite:///test_chat_online.db'
db_module.USE_POSTGRES = False
db_module.DB_FILE = 'test_chat_online.db'
test_db = 'test_chat_online.db'
if os.path.exists(test_db):
    os.remove(test_db)
db_module.init_database()

import auth as auth_module


@pytest.fixture(autouse=True)
def fresh_auth():
    """Clear in-memory codes before each test."""
    auth_module._legacy_codes.clear()
    yield


class TestEmailValidation:
    """Tests for email validation."""

    def test_valid_emails(self):
        valid = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.org',
            'a@b.co',
        ]
        for email in valid:
            assert auth_module.is_valid_email(email) is True, f"Should be valid: {email}"

    def test_invalid_emails(self):
        invalid = [
            'notanemail',
            '@nodomain.com',
            'user@',
            'user@.com',
            '',
            'user name@domain.com',
            'user@domain',
        ]
        for email in invalid:
            assert auth_module.is_valid_email(email) is False, f"Should be invalid: {email}"


class TestVerificationCodes:
    """Tests for verification code generation and validation."""

    def test_generate_code_returns_six_digits(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        user_id = db_module.create_user('codetest', 'codetest@example.com', pw_hash)

        code = auth_module.generate_verification_code(user_id, 'codetest@example.com', 'email_verify')
        assert len(code) == 6
        assert code.isdigit()

    def test_verify_correct_code(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        user_id = db_module.create_user('verifytest', 'vt@example.com', pw_hash)

        code = auth_module.generate_verification_code(user_id, 'vt@example.com', 'email_verify')
        success, message = auth_module.verify_code(user_id, code, 'email_verify')

        assert success is True
        assert 'successful' in message.lower()

    def test_verify_wrong_code(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        user_id = db_module.create_user('wrongcode', 'wc@example.com', pw_hash)

        auth_module.generate_verification_code(user_id, 'wc@example.com', 'email_verify')
        success, message = auth_module.verify_code(user_id, '000000', 'email_verify')

        assert success is False

    def test_verify_invalid_format(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        user_id = db_module.create_user('badformat', 'bf@example.com', pw_hash)

        for bad_code in ['12345', '1234567', 'abc123', '', '12 34']:
            success, _ = auth_module.verify_code(user_id, bad_code, 'email_verify')
            assert success is False, f"Should reject: {bad_code}"


class TestPasswordReset:
    """Tests for password reset token flow."""

    def test_generate_reset_token_for_unknown_email_does_not_leak(self):
        """Unknown email should return None token without raising."""
        token, result = auth_module.generate_password_reset_token('notregistered@example.com')
        assert token is None
        # Should NOT reveal whether email exists
        assert 'registered' in result.lower() or 'sent' in result.lower()

    def test_generate_and_verify_reset_token(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        user_id = db_module.create_user('resetuser', 'reset@example.com', pw_hash)
        user = db_module.get_user_by_email('reset@example.com')

        token, uid = auth_module.generate_password_reset_token('reset@example.com')
        assert token is not None
        assert uid == user_id

        valid, message, verified_uid = auth_module.verify_password_reset_token(token)
        assert valid is True
        assert verified_uid == user_id


class TestSendVerificationEmail:
    """Tests for email sending (when disabled)."""

    def test_send_verification_email_disabled_returns_false(self):
        # With no MAIL_SERVER configured, should return False and print to console
        result = auth_module.send_verification_email('test@example.com', '123456', 'TestUser')
        assert result is False

    def test_send_password_reset_email_disabled_returns_false(self):
        result = auth_module.send_password_reset_email('test@example.com', 'sometoken')
        assert result is False
