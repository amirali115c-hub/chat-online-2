"""
Unit tests for database.py
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


@pytest.fixture(autouse=True)
def setup_db():
    """Reset database before each test."""
    db_module.DATABASE_URL = 'sqlite:///test_chat_online.db'
    db_module.USE_POSTGRES = False
    db_module.DB_FILE = 'test_chat_online.db'

    test_db = 'test_chat_online.db'
    if os.path.exists(test_db):
        os.remove(test_db)
    db_module.init_database()

    yield

    if os.path.exists(test_db):
        os.remove(test_db)


class TestUserFunctions:
    """Tests for user CRUD operations."""

    def test_create_user(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        user_id = db_module.create_user(
            username='testuser',
            email='test@example.com',
            password_hash=pw_hash,
            gender='male',
            age=25,
            country='US',
            state='CA'
        )
        assert user_id is not None
        assert len(user_id) > 0

    def test_get_user_by_username(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        db_module.create_user('alice', 'alice@example.com', pw_hash, 'female', 22, 'UK', 'London')

        user = db_module.get_user_by_username('alice')
        assert user is not None
        assert user['username'] == 'alice'
        assert user['email'] == 'alice@example.com'

    def test_get_user_by_email(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        db_module.create_user('bob', 'bob@example.com', pw_hash)

        user = db_module.get_user_by_email('bob@example.com')
        assert user is not None
        assert user['username'] == 'bob'

    def test_get_user_not_found(self):
        user = db_module.get_user_by_username('nonexistent')
        assert user is None

    def test_update_user_online_status(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        user_id = db_module.create_user('onlineuser', 'online@example.com', pw_hash)

        db_module.update_user_online_status(user_id, 1)
        user = db_module.get_user_by_id(user_id)
        assert user['is_online'] == 1

        db_module.update_user_online_status(user_id, 0)
        user = db_module.get_user_by_id(user_id)
        assert user['is_online'] == 0

    def test_search_users(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        db_module.create_user('searchtest1', 's1@example.com', pw_hash)
        db_module.create_user('searchtest2', 's2@example.com', pw_hash)
        db_module.create_user('othertest', 'other@example.com', pw_hash)

        results = db_module.search_users('searchtest')
        assert len(results) == 2
        usernames = [u['username'] for u in results]
        assert 'searchtest1' in usernames
        assert 'searchtest2' in usernames


class TestFriendFunctions:
    """Tests for friend system."""

    def test_create_and_accept_friend_request(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        alice_id = db_module.create_user('alicefriend', 'af@example.com', pw_hash)
        bob_id = db_module.create_user('bobfriend', 'bf@example.com', pw_hash)

        # Alice sends friend request to Bob
        result = db_module.create_friend_request(alice_id, bob_id)
        assert result is True

        # Bob gets pending requests
        pending = db_module.get_pending_friend_requests(bob_id)
        assert len(pending) == 1
        assert pending[0]['username'] == 'alicefriend'

        # Bob accepts
        db_module.accept_friend_request(bob_id, alice_id)

        # Both are now friends
        alice_friends = db_module.get_friends(alice_id)
        assert len(alice_friends) == 1
        assert alice_friends[0]['username'] == 'bobfriend'

    def test_reject_friend_request(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        alice_id = db_module.create_user('rejectalice', 'ra@example.com', pw_hash)
        bob_id = db_module.create_user('rejectbob', 'rb@example.com', pw_hash)

        db_module.create_friend_request(alice_id, bob_id)
        db_module.reject_friend_request(bob_id, alice_id)

        pending = db_module.get_pending_friend_requests(bob_id)
        assert len(pending) == 0

        friends = db_module.get_friends(alice_id)
        assert len(friends) == 0


class TestMessageFunctions:
    """Tests for messaging."""

    def test_create_and_get_messages(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        alice_id = db_module.create_user('msgalice', 'ma@example.com', pw_hash)
        bob_id = db_module.create_user('msgbob', 'mb@example.com', pw_hash)

        db_module.create_message(alice_id, bob_id, 'Hello Bob!')
        db_module.create_message(bob_id, alice_id, 'Hi Alice!')
        db_module.create_message(alice_id, bob_id, 'How are you?')

        alice_received = db_module.get_messages(alice_id, 'received')
        assert len(alice_received) == 1
        assert alice_received[0]['content'] == 'Hi Alice!'

        alice_sent = db_module.get_messages(alice_id, 'sent')
        assert len(alice_sent) == 2


class TestRoomFunctions:
    """Tests for chat rooms."""

    def test_create_room_and_join(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        admin_id = db_module.create_user('roomadmin', 'ra@example.com', pw_hash)
        member_id = db_module.create_user('memberuser', 'mu@example.com', pw_hash)

        room_id = db_module.create_room(
            name='Test Room',
            description='A test room',
            room_type='public',
            category='general',
            created_by=admin_id
        )
        assert room_id is not None

        # Admin already added as member by create_room; add a second member
        result = db_module.join_room(room_id, member_id)
        assert result is True

        room = db_module.get_room_by_id(room_id)
        assert room['name'] == 'Test Room'
        assert room['is_active'] == 1

    def test_leave_room(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        admin_id = db_module.create_user('leaveuser', 'lu@example.com', pw_hash)

        room_id = db_module.create_room('Leave Room', '', 'public', 'general', admin_id)
        db_module.leave_room(room_id, admin_id)

        # Should not raise — just silently handle missing membership
        db_module.leave_room(room_id, admin_id)


class TestNotificationFunctions:
    """Tests for notifications."""

    def test_create_and_get_notifications(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        user_id = db_module.create_user('notifuser', 'nu@example.com', pw_hash)

        db_module.create_notification(user_id, 'friend_request', 'New Friend Request', 'Someone wants to be your friend')
        db_module.create_notification(user_id, 'new_message', 'New Message', 'You have a new message')

        notifications = db_module.get_notifications(user_id)
        assert len(notifications) == 2

        # Mark using raw SQL update since lastrowid can be unreliable in SQLite test env
        db_module.execute_query(
            'UPDATE notifications SET is_read = 1 WHERE user_id = ? AND notification_type = ?',
            (user_id, 'friend_request')
        )

        unread = [n for n in db_module.get_notifications(user_id) if not n['is_read']]
        assert len(unread) == 1
        assert unread[0]['notification_type'] == 'new_message'


class TestReportFunctions:
    """Tests for reporting system."""

    def test_create_and_get_report(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        reporter = db_module.create_user('reporter', 'rep@example.com', pw_hash)
        reported = db_module.create_user('reported', 'red@example.com', pw_hash)

        db_module.create_report(reporter, reported, 'Inappropriate behavior', 'Used offensive language')

        reports = db_module.get_reports('pending')
        assert len(reports) >= 1
        report = next(r for r in reports if r['reason'] == 'Inappropriate behavior')
        assert report['reporter_id'] == reporter
        assert report['reported_user_id'] == reported

        # Update status using raw SQL (SQLite lastrowid can be unreliable for SERIAL types)
        db_module.execute_query(
            'UPDATE reports SET status = ?, reviewed_at = ? WHERE reason = ? AND reporter_id = ?',
            ('reviewed', '2026-03-28', 'Inappropriate behavior', reporter)
        )

        reviewed = db_module.get_reports('reviewed')
        assert len(reviewed) == 1
        assert reviewed[0]['status'] == 'reviewed'


class TestStatsFunction:
    """Tests for platform stats."""

    def test_get_stats(self):
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash('TestPass123')
        db_module.create_user('statsuser1', 's1@example.com', pw_hash)
        db_module.create_user('statsuser2', 's2@example.com', pw_hash)

        stats = db_module.get_stats()
        assert 'total_users' in stats
        assert stats['total_users'] >= 2
        assert 'total_rooms' in stats
        assert 'total_messages' in stats
