"""
Authentication helpers — email verification, password reset, JWT management.
"""
import secrets
import hashlib
import time
import re
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple

from database import (
    create_verification_code, get_verification_code,
    create_verification_token, get_verification_token,
    mark_user_verified, is_user_verified, get_user_by_id
)
from config import get_config

config = get_config()


# ── Email validation ──────────────────────────────────────────

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email))


# ── Verification code operations ──────────────────────────────

def generate_verification_code(user_id: str, email: str, code_type: str = 'email_verify') -> str:
    """
    Generate a 6-digit verification code and store it in the database.
    Returns the code (to send via email).
    """
    code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    expires_at = datetime.utcnow() + timedelta(minutes=config.VERIFICATION_CODE_EXPIRY)

    try:
        create_verification_code(user_id, code, code_type, expires_at)
    except Exception:
        # Fallback: generate a simple code hash stored in memory (for SQLite without FK)
        _legacy_create_code(user_id, code, code_type, expires_at)

    return code


def verify_code(user_id: str, code: str, code_type: str = 'email_verify') -> Tuple[bool, str]:
    """
    Verify a 6-digit code.
    Returns (success, message).
    """
    if not code or len(code) != 6 or not code.isdigit():
        return False, "Invalid code format."

    try:
        db_code = get_verification_code(user_id, code_type)
    except Exception:
        db_code = _legacy_get_code(user_id, code_type)

    if not db_code:
        return False, "Invalid or expired code."

    # Check expiry
    expires_at = db_code.get('expires_at', '')
    if isinstance(expires_at, str):
        try:
            expires_at = datetime.fromisoformat(expires_at)
        except ValueError:
            return False, "Invalid expiry format."

    if datetime.utcnow() > expires_at:
        return False, "Code has expired. Request a new one."

    # Verify code matches
    stored_code = str(db_code.get('code', ''))
    if not secrets.compare_digest(stored_code, code):
        return False, "Incorrect code."

    return True, "Verification successful."


def generate_password_reset_token(email: str) -> Tuple[Optional[str], str]:
    """
    Generate a secure password reset token for the given email.
    Returns (token, user_id) or (None, error_message).
    """
    if not is_valid_email(email):
        return None, "Invalid email address."

    # Find user by email
    user = None
    try:
        from database import get_user_by_email
        user = get_user_by_email(email)
    except Exception:
        pass

    if not user:
        # Don't reveal whether email exists
        return None, "If that email is registered, a reset link has been sent."

    user_id = user.get('id')
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=config.PASSWORD_RESET_EXPIRY)

    try:
        create_verification_token(user_id, token, 'password_reset', expires_at)
    except Exception:
        return None, "Could not generate token. Please try again."

    return token, user_id


def verify_password_reset_token(token: str) -> Tuple[bool, str, Optional[str]]:
    """
    Verify a password reset token.
    Returns (valid, message, user_id).
    """
    if not token:
        return False, "Invalid token.", None

    try:
        db_token = get_verification_token(token, 'password_reset')
    except Exception:
        return False, "Invalid or expired token.", None

    if not db_token:
        return False, "Invalid or expired token.", None

    expires_at = db_token.get('expires_at', '')
    if isinstance(expires_at, str):
        try:
            expires_at = datetime.fromisoformat(expires_at)
        except ValueError:
            return False, "Invalid expiry.", None

    if datetime.utcnow() > expires_at:
        return False, "Token has expired. Request a new one.", None

    return True, "Token valid.", db_token.get('user_id')


# ── Legacy in-memory code storage (for SQLite setups without FK) ──

_legacy_codes: dict[str, dict] = {}
"""Fallback in-memory store: {f"{user_id}:{code_type}": {"code": ..., "expires_at": ...}}"""


def _legacy_create_code(user_id: str, code: str, code_type: str, expires_at: datetime):
    _legacy_codes[f"{user_id}:{code_type}"] = {
        'code': code,
        'expires_at': expires_at.isoformat()
    }


def _legacy_get_code(user_id: str, code_type: str):
    entry = _legacy_codes.get(f"{user_id}:{code_type}")
    if not entry:
        return None
    return {
        'code': entry['code'],
        'expires_at': entry['expires_at']
    }


# ── Email sending ─────────────────────────────────────────────

def send_verification_email(email: str, code: str, username: str = '') -> bool:
    """
    Send verification email. Returns True if sent, False if failed.
    Configure MAIL_* settings in .env to enable.
    """
    if not config.MAIL_SERVER:
        print(f"[EMAIL DISABLED] Verification code for {email}: {code}")
        return False

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg['From'] = config.MAIL_USERNAME
        msg['To'] = email
        msg['Subject'] = "Verify your ChatOnline account"

        body = f"""
Hi{(' ' + username) if username else ''},

Your verification code is: {code}

Enter this code to verify your account. It expires in {config.VERIFICATION_CODE_EXPIRY} minutes.

— The ChatOnline Team
        """.strip()

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT) as server:
            if config.MAIL_USE_TLS:
                server.starttls()
            if config.MAIL_USERNAME and config.MAIL_PASSWORD:
                server.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
            server.sendmail(config.MAIL_USERNAME, [email], msg.as_string())

        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {email}: {e}")
        return False


def send_password_reset_email(email: str, token: str) -> bool:
    """
    Send password reset email. Returns True if sent.
    """
    if not config.MAIL_SERVER:
        reset_url = f"http://localhost:{os.environ.get('PORT', 5001)}/reset-password?token={token}"
        print(f"[EMAIL DISABLED] Password reset for {email}: {reset_url}")
        return False

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg['From'] = config.MAIL_USERNAME
        msg['To'] = email
        msg['Subject'] = "Reset your ChatOnline password"

        reset_url = f"http://localhost:{os.environ.get('PORT', 5001)}/reset-password?token={token}"

        body = f"""
Click the link below to reset your password (expires in {config.PASSWORD_RESET_EXPIRY} minutes):

{reset_url}

If you didn't request this, ignore this email.

— The ChatOnline Team
        """.strip()

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT) as server:
            if config.MAIL_USE_TLS:
                server.starttls()
            if config.MAIL_USERNAME and config.MAIL_PASSWORD:
                server.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
            server.sendmail(config.MAIL_USERNAME, [email], msg.as_string())

        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send password reset to {email}: {e}")
        return False
