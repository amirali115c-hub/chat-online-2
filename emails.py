# Email Notification Module
# For now - simulating email sends (can be connected to real SMTP later)

class EmailNotifier:
    def __init__(self):
        # Email configuration (can be updated later)
        self.smtp_host = None
        self.smtp_port = 587
        self.smtp_user = None
        self.smtp_password = None
        self.from_email = "noreply@chatonline.com"

    def send_welcome_email(self, email, username):
        """Send welcome email to new user"""
        subject = "Welcome to Chat Online!"
        body = f"""
        Hi {username},

        Welcome to Chat Online! We're excited to have you join our community.

        Start chatting with strangers and make new friends today!

        Get started: http://127.0.0.1:5001

        Best regards,
        The Chat Online Team
        """
        return self._send(email, subject, body)

    def send_password_reset_email(self, email, reset_token):
        """Send password reset email"""
        subject = "Password Reset - Chat Online"
        body = f"""
        You requested a password reset for your Chat Online account.

        Click the link below to reset your password:
        http://127.0.0.1:5001/reset-password?token={reset_token}

        This link will expire in 1 hour.

        If you didn't request this, please ignore this email.

        Best regards,
        The Chat Online Team
        """
        return self._send(email, subject, body)

    def send_friend_request_email(self, email, from_username):
        """Send friend request notification"""
        subject = f"{from_username} sent you a friend request"
        body = f"""
        Hi,

        {from_username} sent you a friend request on Chat Online!

        Log in to accept or decline: http://127.0.0.1:5001/friends

        Best regards,
        The Chat Online Team
        """
        return self._send(email, subject, body)

    def send_new_message_email(self, email, from_username):
        """Send new message notification"""
        subject = f"New message from {from_username}"
        body = f"""
        Hi,

        You have a new message from {from_username} on Chat Online!

        Log in to read: http://127.0.0.1:5001/inbox

        Best regards,
        The Chat Online Team
        """
        return self._send(email, subject, body)

    def _send(self, to_email, subject, body):
        """Send email (simulated for now)"""
        # In production, connect to real SMTP server
        # For now, just log the email
        print(f"[EMAIL] To: {to_email}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Body: {body[:100]}...")
        return True

    def configure(self, smtp_host, smtp_port, smtp_user, smtp_password, from_email):
        """Configure SMTP settings"""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email

# Global email notifier
email_notifier = EmailNotifier()
