# User Verification Module
import uuid
import hashlib
from datetime import datetime, timedelta
from database import get_db

class VerificationManager:
    def __init__(self):
        pass

    def generate_verification_code(self, user_id):
        """Generate email verification code"""
        code = str(uuid.uuid4())[:8]

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO verification_codes (user_id, code, type, expires_at)
                VALUES (?, ?, 'email', ?)
            ''', (user_id, code, (datetime.utcnow() + timedelta(days=7)).isoformat()))
            conn.commit()

        return code

    def verify_email(self, code):
        """Verify email with code"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM verification_codes
                WHERE code = ? AND type = 'email' AND expires_at > ?
            ''', (code, datetime.utcnow().isoformat()))

            row = cursor.fetchone()
            if not row:
                return False, "Invalid or expired code"

            user_id = row['user_id']

            # Mark user as verified
            cursor.execute('UPDATE users SET is_verified = 1 WHERE id = ?', (user_id,))

            # Delete used code
            cursor.execute('DELETE FROM verification_codes WHERE code = ?', (code,))
            conn.commit()

            return True, "Email verified successfully"

    def generate_password_reset_token(self, email):
        """Generate password reset token"""
        token = str(uuid.uuid4())
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        with get_db() as conn:
            cursor = conn.cursor()

            # Find user
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()

            if not row:
                return None

            user_id = row['id']

            # Store token
            cursor.execute('''
                INSERT INTO verification_tokens (user_id, token, type, expires_at)
                VALUES (?, ?, 'password_reset', ?)
            ''', (user_id, token_hash, (datetime.utcnow() + timedelta(hours=1)).isoformat()))
            conn.commit()

        return token

    def verify_password_reset(self, token):
        """Verify password reset token"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM verification_tokens
                WHERE token = ? AND type = 'password_reset' AND expires_at > ?
            ''', (token_hash, datetime.utcnow().isoformat()))

            row = cursor.fetchone()
            if not row:
                return None

            return row['user_id']

    def reset_password(self, user_id, new_password):
        """Reset user password"""
        from werkzeug.security import generate_password_hash

        password_hash = generate_password_hash(new_password)

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))

            # Delete used tokens
            cursor.execute('DELETE FROM verification_tokens WHERE user_id = ? AND type = ?', (user_id, 'password_reset'))
            conn.commit()

        return True

# Verification instance
verification = VerificationManager()
