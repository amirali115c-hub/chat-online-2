import sqlite3
import uuid
from datetime import datetime
from contextlib import contextmanager

# Database file
DB_FILE = 'chat_online.db'

@contextmanager
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize database tables"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT,
                gender TEXT,
                age INTEGER,
                country TEXT,
                state TEXT,
                bio TEXT,
                avatar TEXT,
                is_online INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                is_verified INTEGER DEFAULT 0,
                last_seen TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id TEXT NOT NULL,
                receiver_id TEXT,
                room_id TEXT,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                is_read INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (receiver_id) REFERENCES users (id)
            )
        ''')

        # Friends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                friend_id TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (friend_id) REFERENCES users (id),
                UNIQUE(user_id, friend_id)
            )
        ''')

        # Rooms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                room_type TEXT DEFAULT 'public',
                category TEXT,
                icon TEXT DEFAULT 'comments',
                gradient TEXT DEFAULT 'linear-gradient(135deg, #8B5CF6, #EC4899)',
                is_active INTEGER DEFAULT 1,
                created_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')

        # Room members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS room_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT DEFAULT 'member',
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES rooms (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(room_id, user_id)
            )
        ''')

        # Room messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS room_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES rooms (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                link TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id TEXT NOT NULL,
                reported_user_id TEXT,
                reason TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                reviewed_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reporter_id) REFERENCES users (id),
                FOREIGN KEY (reported_user_id) REFERENCES users (id)
            )
        ''')

        # Verification codes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                code TEXT NOT NULL,
                type TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Verification tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                token TEXT NOT NULL,
                type TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_room ON messages(room_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at)')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_friends_user ON friends(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_friends_friend ON friends(friend_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_friends_status ON friends(status)')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_room_members_room ON room_members(room_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_room_members_user ON room_members(user_id)')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_room_messages_room ON room_messages(room_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_room_messages_user ON room_messages(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_room_messages_created ON room_messages(created_at)')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read)')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_reporter ON reports(reporter_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_reported ON reports(reported_user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_verification_codes_user ON verification_codes(user_id)')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_online ON users(is_online)')

        conn.commit()
        print("Database initialized successfully!")

# ==================== USER FUNCTIONS ====================

def create_user(username, email, password_hash, gender=None, age=None, country=None, state=None):
    """Create a new user"""
    user_id = str(uuid.uuid4())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (id, username, email, password_hash, gender, age, country, state)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, email, password_hash, gender, age, country, state))
        conn.commit()
        return user_id

def get_user_by_id(user_id):
    """Get user by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_username(username):
    """Get user by username"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_email(email):
    """Get user by email"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_user_online_status(user_id, is_online):
    """Update user's online status"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET is_online = ?, last_seen = ? WHERE id = ?
        ''', (is_online, datetime.utcnow().isoformat(), user_id))
        conn.commit()

def search_users(query, limit=20):
    """Search users by username"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM users WHERE username LIKE ? LIMIT ?
        ''', (f'%{query}%', limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# ==================== MESSAGE FUNCTIONS ====================

def create_message(sender_id, receiver_id, content, room_id=None):
    """Create a new message"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (sender_id, receiver_id, room_id, content)
            VALUES (?, ?, ?, ?)
        ''', (sender_id, receiver_id, room_id, content))
        conn.commit()
        return cursor.lastrowid

def get_messages(user_id, message_type='received', limit=50):
    """Get user's messages"""
    with get_db() as conn:
        cursor = conn.cursor()
        if message_type == 'received':
            cursor.execute('''
                SELECT * FROM messages WHERE receiver_id = ?
                ORDER BY created_at DESC LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM messages WHERE sender_id = ?
                ORDER BY created_at DESC LIMIT ?
            ''', (user_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# ==================== FRIEND FUNCTIONS ====================

def create_friend_request(user_id, friend_id):
    """Create a friend request"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO friends (user_id, friend_id, status)
                VALUES (?, ?, 'pending')
            ''', (user_id, friend_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def get_friends(user_id):
    """Get user's friends"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.* FROM users u
            JOIN friends f ON (f.friend_id = u.id OR f.user_id = u.id)
            WHERE (f.user_id = ? OR f.friend_id = ?) AND f.status = 'accepted' AND u.id != ?
        ''', (user_id, user_id, user_id))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_pending_friend_requests(user_id):
    """Get pending friend requests"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, f.id as request_id, f.created_at as request_time
            FROM users u
            JOIN friends f ON f.user_id = u.id
            WHERE f.friend_id = ? AND f.status = 'pending'
        ''', (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def accept_friend_request(user_id, requester_id):
    """Accept a friend request"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE friends SET status = 'accepted'
            WHERE user_id = ? AND friend_id = ?
        ''', (requester_id, user_id))
        conn.commit()

def reject_friend_request(user_id, requester_id):
    """Reject a friend request"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM friends WHERE user_id = ? AND friend_id = ? AND status = 'pending'
        ''', (requester_id, user_id))
        conn.commit()

# ==================== ROOM FUNCTIONS ====================

def create_room(name, description, room_type, category, created_by):
    """Create a new room"""
    room_id = str(uuid.uuid4())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO rooms (id, name, description, room_type, category, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (room_id, name, description, room_type, category, created_by))

        # Add creator as admin
        cursor.execute('''
            INSERT INTO room_members (room_id, user_id, role)
            VALUES (?, ?, 'admin')
        ''', (room_id, created_by))

        conn.commit()
        return room_id

def get_rooms(category='all'):
    """Get all rooms"""
    with get_db() as conn:
        cursor = conn.cursor()
        if category == 'all':
            cursor.execute('SELECT * FROM rooms WHERE is_active = 1')
        else:
            cursor.execute('SELECT * FROM rooms WHERE category = ? AND is_active = 1', (category,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_room_by_id(room_id):
    """Get room by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rooms WHERE id = ?', (room_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def join_room(room_id, user_id):
    """Join a room"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO room_members (room_id, user_id, role)
                VALUES (?, ?, 'member')
            ''', (room_id, user_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def leave_room(room_id, user_id):
    """Leave a room"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM room_members WHERE room_id = ? AND user_id = ?
        ''', (room_id, user_id))
        conn.commit()

def get_room_messages(room_id, limit=50):
    """Get room messages"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT rm.*, u.username, u.gender FROM room_messages rm
            JOIN users u ON rm.user_id = u.id
            WHERE rm.room_id = ?
            ORDER BY rm.created_at DESC LIMIT ?
        ''', (room_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def create_room_message(room_id, user_id, content):
    """Create a room message"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO room_messages (room_id, user_id, content)
            VALUES (?, ?, ?)
        ''', (room_id, user_id, content))
        conn.commit()
        return cursor.lastrowid

# ==================== NOTIFICATION FUNCTIONS ====================

def create_notification(user_id, notification_type, title, content, link=None):
    """Create a notification"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (user_id, notification_type, title, content, link)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, notification_type, title, content, link))
        conn.commit()

def get_notifications(user_id, limit=20):
    """Get user notifications"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM notifications WHERE user_id = ?
            ORDER BY created_at DESC LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def mark_notification_read(notification_id, user_id):
    """Mark notification as read"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE notifications SET is_read = 1
            WHERE id = ? AND user_id = ?
        ''', (notification_id, user_id))
        conn.commit()

# ==================== STATS FUNCTIONS ====================

def get_stats():
    """Get platform statistics"""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as count FROM users')
        total_users = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_online = 1')
        online_users = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM rooms WHERE is_active = 1')
        total_rooms = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM messages')
        total_messages = cursor.fetchone()['count']

        return {
            'total_users': total_users,
            'online_users': online_users,
            'total_rooms': total_rooms,
            'total_messages': total_messages
        }

# Initialize database on import
if __name__ == '__main__':
    init_database()
