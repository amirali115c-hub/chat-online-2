"""
Chat Online Database Module
Supports both SQLite (local) and PostgreSQL (production)
"""
import os
import sqlite3
import uuid
from datetime import datetime
from contextlib import contextmanager

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')

# Determine which database to use
USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        print("Using PostgreSQL database")
    except ImportError:
        print("WARNING: psycopg2 not installed, falling back to SQLite")
        USE_POSTGRES = False
        DB_FILE = os.environ.get('DB_FILE', 'chat_online.db')
else:
    DB_FILE = os.environ.get('DB_FILE', 'chat_online.db')
    print(f"Using SQLite database: {DB_FILE}")

# ==================== DATABASE CONNECTION ====================

@contextmanager
def get_db():
    """Get database connection"""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        try:
            yield conn
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

def dict_from_row(row):
    """Convert row to dictionary"""
    if row is None:
        return None
    if hasattr(row, 'keys'):
        return dict(row)
    return row

# ==================== INITIALIZATION ====================

def init_database():
    """Initialize database tables"""
    with get_db() as conn:
        if USE_POSTGRES:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                sender_id TEXT NOT NULL,
                receiver_id TEXT,
                room_id TEXT,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users (id),
                FOREIGN KEY (receiver_id) REFERENCES users (id)
            )
        ''')

        # Friends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                friend_id TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')

        # Room members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS room_members (
                id SERIAL PRIMARY KEY,
                room_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT DEFAULT 'member',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES rooms (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(room_id, user_id)
            )
        ''')

        # Room messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS room_messages (
                id SERIAL PRIMARY KEY,
                room_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES rooms (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                link TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id SERIAL PRIMARY KEY,
                reporter_id TEXT NOT NULL,
                reported_user_id TEXT,
                reason TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                reviewed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reporter_id) REFERENCES users (id),
                FOREIGN KEY (reported_user_id) REFERENCES users (id)
            )
        ''')

        # Verification codes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_codes (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                code TEXT NOT NULL,
                type TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Verification tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_tokens (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                token TEXT NOT NULL,
                type TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Create indexes
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

        if not USE_POSTGRES:
            conn.commit()

        print("Database initialized successfully!")

# ==================== HELPER FUNCTIONS ====================

def execute_query(query, params=(), fetch=False):
    """Execute a query and optionally fetch results"""
    with get_db() as conn:
        if USE_POSTGRES:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        
        cursor.execute(query, params)
        
        if fetch:
            rows = cursor.fetchall()
            if USE_POSTGRES:
                return [dict(row) for row in rows]
            return [dict(row) for row in rows]
        
        if not USE_POSTGRES:
            conn.commit()
        
        return cursor.lastrowid if hasattr(cursor, 'lastrowid') else None

def fetch_one(query, params=()):
    """Fetch a single row"""
    with get_db() as conn:
        if USE_POSTGRES:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        if USE_POSTGRES:
            return dict(row)
        return dict(row)

def fetch_all(query, params=()):
    """Fetch all rows"""
    with get_db() as conn:
        if USE_POSTGRES:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        if USE_POSTGRES:
            return [dict(row) for row in rows]
        return [dict(row) for row in rows]

# ==================== USER FUNCTIONS ====================

def create_user(username, email, password_hash, gender=None, age=None, country=None, state=None):
    """Create a new user"""
    user_id = str(uuid.uuid4())
    if USE_POSTGRES:
        execute_query('''
            INSERT INTO users (id, username, email, password_hash, gender, age, country, state)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, username, email, password_hash, gender, age, country, state))
    else:
        execute_query('''
            INSERT INTO users (id, username, email, password_hash, gender, age, country, state)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, email, password_hash, gender, age, country, state))
    return user_id

def get_user_by_id(user_id):
    """Get user by ID"""
    return fetch_one('SELECT * FROM users WHERE id = %s' if USE_POSTGRES else 'SELECT * FROM users WHERE id = ?', (user_id,))

def get_user_by_username(username):
    """Get user by username"""
    return fetch_one('SELECT * FROM users WHERE username = %s' if USE_POSTGRES else 'SELECT * FROM users WHERE username = ?', (username,))

def get_user_by_email(email):
    """Get user by email"""
    return fetch_one('SELECT * FROM users WHERE email = %s' if USE_POSTGRES else 'SELECT * FROM users WHERE email = ?', (email,))

def update_user_online_status(user_id, is_online):
    """Update user's online status"""
    execute_query('''
        UPDATE users SET is_online = %s, last_seen = %s WHERE id = %s
    ''' if USE_POSTGRES else '''
        UPDATE users SET is_online = ?, last_seen = ? WHERE id = ?
    ''', (is_online, datetime.utcnow().isoformat(), user_id))

def search_users(query, limit=20):
    """Search users by username"""
    return fetch_all(
        'SELECT * FROM users WHERE username LIKE %s LIMIT %s' if USE_POSTGRES else 'SELECT * FROM users WHERE username LIKE ? LIMIT ?',
        (f'%{query}%', limit)
    )

# ==================== MESSAGE FUNCTIONS ====================

def create_message(sender_id, receiver_id, content, room_id=None):
    """Create a new message"""
    return execute_query('''
        INSERT INTO messages (sender_id, receiver_id, room_id, content)
        VALUES (%s, %s, %s, %s)
    ''' if USE_POSTGRES else '''
        INSERT INTO messages (sender_id, receiver_id, room_id, content)
        VALUES (?, ?, ?, ?)
    ''', (sender_id, receiver_id, room_id, content))

def get_messages(user_id, message_type='received', limit=50):
    """Get user's messages"""
    if message_type == 'received':
        return fetch_all(
            'SELECT * FROM messages WHERE receiver_id = %s ORDER BY created_at DESC LIMIT %s' if USE_POSTGRES else 'SELECT * FROM messages WHERE receiver_id = ? ORDER BY created_at DESC LIMIT ?',
            (user_id, limit)
        )
    else:
        return fetch_all(
            'SELECT * FROM messages WHERE sender_id = %s ORDER BY created_at DESC LIMIT %s' if USE_POSTGRES else 'SELECT * FROM messages WHERE sender_id = ? ORDER BY created_at DESC LIMIT ?',
            (user_id, limit)
        )

# ==================== FRIEND FUNCTIONS ====================

def create_friend_request(user_id, friend_id):
    """Create a friend request"""
    try:
        execute_query('''
            INSERT INTO friends (user_id, friend_id, status)
            VALUES (%s, %s, 'pending')
        ''' if USE_POSTGRES else '''
            INSERT INTO friends (user_id, friend_id, status)
            VALUES (?, ?, 'pending')
        ''', (user_id, friend_id))
        return True
    except Exception:
        return False

def get_friends(user_id):
    """Get user's friends"""
    return fetch_all('''
        SELECT u.* FROM users u
        JOIN friends f ON (f.friend_id = u.id OR f.user_id = u.id)
        WHERE (f.user_id = %s OR f.friend_id = %s) AND f.status = 'accepted' AND u.id != %s
    ''' if USE_POSTGRES else '''
        SELECT u.* FROM users u
        JOIN friends f ON (f.friend_id = u.id OR f.user_id = u.id)
        WHERE (f.user_id = ? OR f.friend_id = ?) AND f.status = 'accepted' AND u.id != ?
    ''', (user_id, user_id, user_id))

def get_pending_friend_requests(user_id):
    """Get pending friend requests"""
    return fetch_all('''
        SELECT u.*, f.id as request_id, f.created_at as request_time
        FROM users u
        JOIN friends f ON f.user_id = u.id
        WHERE f.friend_id = %s AND f.status = 'pending'
    ''' if USE_POSTGRES else '''
        SELECT u.*, f.id as request_id, f.created_at as request_time
        FROM users u
        JOIN friends f ON f.user_id = u.id
        WHERE f.friend_id = ? AND f.status = 'pending'
    ''', (user_id,))

def accept_friend_request(user_id, requester_id):
    """Accept a friend request"""
    execute_query('''
        UPDATE friends SET status = 'accepted'
        WHERE user_id = %s AND friend_id = %s
    ''' if USE_POSTGRES else '''
        UPDATE friends SET status = 'accepted'
        WHERE user_id = ? AND friend_id = ?
    ''', (requester_id, user_id))

def reject_friend_request(user_id, requester_id):
    """Reject a friend request"""
    execute_query('''
        DELETE FROM friends WHERE user_id = %s AND friend_id = %s AND status = 'pending'
    ''' if USE_POSTGRES else '''
        DELETE FROM friends WHERE user_id = ? AND friend_id = ? AND status = 'pending'
    ''', (requester_id, user_id))

# ==================== ROOM FUNCTIONS ====================

def create_room(name, description, room_type, category, created_by):
    """Create a new room"""
    room_id = str(uuid.uuid4())
    execute_query('''
        INSERT INTO rooms (id, name, description, room_type, category, created_by)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''' if USE_POSTGRES else '''
        INSERT INTO rooms (id, name, description, room_type, category, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (room_id, name, description, room_type, category, created_by))

    # Add creator as admin
    execute_query('''
        INSERT INTO room_members (room_id, user_id, role)
        VALUES (%s, %s, 'admin')
    ''' if USE_POSTGRES else '''
        INSERT INTO room_members (room_id, user_id, role)
        VALUES (?, ?, 'admin')
    ''', (room_id, created_by))

    return room_id

def get_rooms(category='all'):
    """Get all rooms"""
    if category == 'all':
        return fetch_all('SELECT * FROM rooms WHERE is_active = 1')
    return fetch_all(
        'SELECT * FROM rooms WHERE category = %s AND is_active = 1' if USE_POSTGRES else 'SELECT * FROM rooms WHERE category = ? AND is_active = 1',
        (category,)
    )

def get_room_by_id(room_id):
    """Get room by ID"""
    return fetch_one('SELECT * FROM rooms WHERE id = %s' if USE_POSTGRES else 'SELECT * FROM rooms WHERE id = ?', (room_id,))

def join_room(room_id, user_id):
    """Join a room"""
    try:
        execute_query('''
            INSERT INTO room_members (room_id, user_id, role)
            VALUES (%s, %s, 'member')
        ''' if USE_POSTGRES else '''
            INSERT INTO room_members (room_id, user_id, role)
            VALUES (?, ?, 'member')
        ''', (room_id, user_id))
        return True
    except Exception:
        return False

def leave_room(room_id, user_id):
    """Leave a room"""
    execute_query('''
        DELETE FROM room_members WHERE room_id = %s AND user_id = %s
    ''' if USE_POSTGRES else '''
        DELETE FROM room_members WHERE room_id = ? AND user_id = ?
    ''', (room_id, user_id))

def get_room_messages(room_id, limit=50):
    """Get room messages"""
    return fetch_all('''
        SELECT rm.*, u.username, u.gender FROM room_messages rm
        JOIN users u ON rm.user_id = u.id
        WHERE rm.room_id = %s
        ORDER BY rm.created_at DESC LIMIT %s
    ''' if USE_POSTGRES else '''
        SELECT rm.*, u.username, u.gender FROM room_messages rm
        JOIN users u ON rm.user_id = u.id
        WHERE rm.room_id = ?
        ORDER BY rm.created_at DESC LIMIT ?
    ''', (room_id, limit))

def create_room_message(room_id, user_id, content):
    """Create a room message"""
    return execute_query('''
        INSERT INTO room_messages (room_id, user_id, content)
        VALUES (%s, %s, %s)
    ''' if USE_POSTGRES else '''
        INSERT INTO room_messages (room_id, user_id, content)
        VALUES (?, ?, ?)
    ''', (room_id, user_id, content))

# ==================== NOTIFICATION FUNCTIONS ====================

def create_notification(user_id, notification_type, title, content, link=None):
    """Create a notification"""
    execute_query('''
        INSERT INTO notifications (user_id, notification_type, title, content, link)
        VALUES (%s, %s, %s, %s, %s)
    ''' if USE_POSTGRES else '''
        INSERT INTO notifications (user_id, notification_type, title, content, link)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, notification_type, title, content, link))

def get_notifications(user_id, limit=20):
    """Get user notifications"""
    return fetch_all('''
        SELECT * FROM notifications WHERE user_id = %s
        ORDER BY created_at DESC LIMIT %s
    ''' if USE_POSTGRES else '''
        SELECT * FROM notifications WHERE user_id = ?
        ORDER BY created_at DESC LIMIT ?
    ''', (user_id, limit))

def mark_notification_read(notification_id, user_id):
    """Mark notification as read"""
    execute_query('''
        UPDATE notifications SET is_read = 1
        WHERE id = %s AND user_id = %s
    ''' if USE_POSTGRES else '''
        UPDATE notifications SET is_read = 1
        WHERE id = ? AND user_id = ?
    ''', (notification_id, user_id))

# ==================== STATS FUNCTIONS ====================

def get_stats():
    """Get platform statistics"""
    total_users = fetch_one('SELECT COUNT(*) as count FROM users')
    online_users = fetch_one('SELECT COUNT(*) as count FROM users WHERE is_online = 1')
    total_rooms = fetch_one('SELECT COUNT(*) as count FROM rooms WHERE is_active = 1')
    total_messages = fetch_one('SELECT COUNT(*) as count FROM messages')

    return {
        'total_users': total_users['count'] if total_users else 0,
        'online_users': online_users['count'] if online_users else 0,
        'total_rooms': total_users['count'] if total_rooms else 0,
        'total_messages': total_messages['count'] if total_messages else 0
    }

# Initialize database on import
if __name__ == '__main__':
    init_database()
