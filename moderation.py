# Moderation & Content Filtering Module
import re
from datetime import datetime, timedelta

class ModerationManager:
    def __init__(self):
        # Bad words list (can be expanded)
        self.bad_words = [
            'spam', 'scam', 'fake', 'hack', 'crack',
            # Add more as needed
        ]

        # Suspicious patterns
        self.suspicious_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'\b\d{10,}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
        ]

    def check_message(self, message):
        """Check a message for violations"""
        issues = []

        # Check for bad words
        message_lower = message.lower()
        found_words = [word for word in self.bad_words if word in message_lower]
        if found_words:
            issues.append({
                'type': 'bad_words',
                'severity': 'medium',
                'details': f'Found inappropriate words: {", ".join(found_words)}'
            })

        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, message):
                issues.append({
                    'type': 'suspicious_pattern',
                    'severity': 'low',
                    'details': 'Contains suspicious pattern (link/phone/email)'
                })
                break

        # Check message length
        if len(message) > 1000:
            issues.append({
                'type': 'too_long',
                'severity': 'low',
                'details': 'Message too long'
            })

        return {
            'allowed': len(issues) == 0,
            'issues': issues
        }

    def check_user_content(self, username, bio=None):
        """Check user profile content"""
        issues = []

        username_lower = username.lower()
        found_words = [word for word in self.bad_words if word in username_lower]
        if found_words:
            issues.append({
                'type': 'bad_words',
                'severity': 'high',
                'field': 'username',
                'details': f'Username contains inappropriate words'
            })

        if bio:
            bio_lower = bio.lower()
            found_words = [word for word in self.bad_words if word in bio_lower]
            if found_words:
                issues.append({
                    'type': 'bad_words',
                    'severity': 'medium',
                    'field': 'bio',
                    'details': f'Bio contains inappropriate words'
                })

        return {
            'allowed': len(issues) == 0,
            'issues': issues
        }

    def auto_moderate(self, message):
        """Auto-moderate a message"""
        result = self.check_message(message)

        if not result['allowed']:
            # Log for review but don't block
            severity = max([issue['severity'] for issue in result['issues']], default='low')
            return {
                'action': 'flag' if severity == 'low' else 'block',
                'reason': result['issues'][0]['details'] if result['issues'] else 'Content violation'
            }

        return {'action': 'allow'}

# Global moderation manager
moderation = ModerationManager()
