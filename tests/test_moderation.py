"""
Unit tests for moderation.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import moderation as mod_module


@pytest.fixture
def mod():
    return mod_module.moderation


class TestMessageModeration:
    """Tests for message content moderation."""

    def test_clean_message_allowed(self, mod):
        result = mod.check_message('Hello, how are you today?')
        assert result['allowed'] is True
        assert len(result['issues']) == 0

    def test_profanity_flagged(self, mod):
        # 'spam' is in the bad words list
        result = mod.check_message('This is spam content')
        assert result['allowed'] is False
        assert any(i['type'] == 'bad_words' for i in result['issues'])

    def test_url_flagged_as_suspicious(self, mod):
        result = mod.check_message('Check out https://example.com/malware')
        assert result['allowed'] is False
        assert any(i['type'] == 'suspicious_pattern' for i in result['issues'])

    def test_phone_number_flagged(self, mod):
        result = mod.check_message('Call me at 12345678901')
        assert result['allowed'] is False
        assert any(i['type'] == 'suspicious_pattern' for i in result['issues'])

    def test_email_address_flagged(self, mod):
        result = mod.check_message('Email me at john@unknownsite.com')
        assert result['allowed'] is False
        assert any(i['type'] == 'suspicious_pattern' for i in result['issues'])

    def test_very_long_message_flagged(self, mod):
        long_msg = 'a' * 1001
        result = mod.check_message(long_msg)
        assert result['allowed'] is False
        assert any(i['type'] == 'too_long' for i in result['issues'])

    def test_empty_message_allowed(self, mod):
        result = mod.check_message('')
        assert result['allowed'] is True

    def test_multiple_issues_reported(self, mod):
        result = mod.check_message('spam ' + 'https://evil.com ' * 1 + 'a' * 1001)
        assert result['allowed'] is False
        assert len(result['issues']) >= 2


class TestAutoModerate:
    """Tests for auto-moderation decisions."""

    def test_auto_allow_clean(self, mod):
        result = mod.auto_moderate('Hello friend, how is your day going?')
        assert result['action'] == 'allow'

    def test_auto_block_medium_severity(self, mod):
        # 'spam' = medium severity bad_words; https://example.com = low severity suspicious_pattern
        # max(medium, low) = medium -> action = 'block'
        result = mod.auto_moderate('spam https://example.com')
        assert result['action'] == 'block'


class TestUserContentModeration:
    """Tests for user profile content checks."""

    def test_clean_username_allowed(self, mod):
        result = mod.check_user_content('cooluser123')
        assert result['allowed'] is True

    def test_profane_username_rejected(self, mod):
        result = mod.check_user_content('spammer99')
        assert result['allowed'] is False
        assert any(i['field'] == 'username' for i in result['issues'])

    def test_clean_bio_allowed(self, mod):
        result = mod.check_user_content('realuser', bio='I love coding and coffee')
        assert result['allowed'] is True

    def test_profane_bio_rejected(self, mod):
        result = mod.check_user_content('realuser', bio='This is not a scam')
        assert result['allowed'] is False
        assert any(i['field'] == 'bio' for i in result['issues'])

    def test_none_bio_handled(self, mod):
        result = mod.check_user_content('someuser', bio=None)
        assert result['allowed'] is True
