# Admin & Moderation Module
import sqlite3
import uuid
from datetime import datetime, timedelta
from database import get_db

class AdminManager:
    def __init__(self):
        self.db = get_db

    # ============ USER MANAGEMENT ============

    def get_all_users(self, limit=50, offset=0):
        """Get all users with pagination"""
        with self.db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM users
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        with self.db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def search_users(self, query, limit=20):
        """Search users by username or email"""
        with self.db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM users
                WHERE username LIKE ? OR email LIKE ?
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_user_status(self, user_id, is_banned=False, is_verified=False):
        """Update user status"""
        with self.db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET is_banned = ?, is_verified = ?
                WHERE id = ?
            ''', (is_banned, is_verified, user_id))
            conn.commit()

    def delete_user(self, user_id):
        """Delete a user"""
        with self.db() as conn:
            cursor = conn.cursor()
            # Delete related records first
            cursor.execute('DELETE FROM messages WHERE sender_id = ? OR receiver_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM friends WHERE user_id = ? OR friend_id = ?', (user_id, user_id))
            cursor.execute('DELETE FROM notifications WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()

    # ============ MESSAGE MANAGEMENT ============

    def get_recent_messages(self, limit=100):
        """Get recent messages"""
        with self.db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.*, u1.username as sender_name, u2.username as receiver_name
                FROM messages m
                LEFT JOIN users u1 ON m.sender_id = u1.id
                LEFT JOIN users u2 ON m.receiver_id = u2.id
                ORDER BY m.created_at DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def delete_message(self, message_id):
        """Delete a message"""
        with self.db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages WHERE id = ?', (message_id,))
            conn.commit()

    def search_messages(self, query, limit=50):
        """Search messages"""
        with self.db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.*, u1.username as sender_name
                FROM messages m
                LEFT JOIN users u1 ON m.sender_id = u1.id
                WHERE m.content LIKE ?
                ORDER BY m.created_at DESC
                LIMIT ?
            ''', (f'%{query}%', limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    # ============ REPORTS MANAGEMENT ============

    def get_all_reports(self, status='pending', limit=50):
        """Get all reports"""
        with self.db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.*, u1.username as reporter_name, u2.username as reported_name
                FROM reports r
                LEFT JOIN users u1 ON r.reporter_id = u1.id
                LEFT JOIN users u2 ON r.reported_user_id = u2.id
                WHERE r.status = ?
                ORDER BY r.created_at DESC
                LIMIT ?
            ''', (status, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_report_status(self, report_id, status):
        """Update report status"""
        with self.db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE reports SET status = ?, reviewed_at = ?
                WHERE id = ?
            ''', (status, datetime.utcnow().isoformat(), report_id))
            conn.commit()

    # ============ STATISTICS ============

    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        with self.db() as conn:
            cursor = conn.cursor()

            # Total users
            cursor.execute('SELECT COUNT(*) as count FROM users')
            total_users = cursor.fetchone()['count']

            # Online users
            cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_online = 1')
            online_users = cursor.fetchone()['count']

            # Total messages
            cursor.execute('SELECT COUNT(*) as count FROM messages')
            total_messages = cursor.fetchone()['count']

            # Today's messages
            today = datetime.utcnow().date().isoformat()
            cursor.execute('SELECT COUNT(*) as count FROM messages WHERE created_at LIKE ?', (f'{today}%',))
            today_messages = cursor.fetchone()['count']

            # Total rooms
            cursor.execute('SELECT COUNT(*) as count FROM rooms WHERE is_active = 1')
            total_rooms = cursor.fetchone()['count']

            # Pending reports
            cursor.execute("SELECT COUNT(*) as count FROM reports WHERE status = 'pending'")
            pending_reports = cursor.fetchone()['count']

            # New users today
            cursor.execute('SELECT COUNT(*) as count FROM users WHERE created_at LIKE ?', (f'{today}%',))
            new_users_today = cursor.fetchone()['count']

            return {
                'total_users': total_users,
                'online_users': online_users,
                'total_messages': total_messages,
                'today_messages': today_messages,
                'total_rooms': total_rooms,
                'pending_reports': pending_reports,
                'new_users_today': new_users_today
            }

    def get_activity_stats(self, days=7):
        """Get activity stats for last N days"""
        stats = []
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).date().isoformat()

            with self.db() as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT COUNT(*) as count FROM users WHERE created_at LIKE ?', (f'{date}%',))
                new_users = cursor.fetchone()['count']

                cursor.execute('SELECT COUNT(*) as count FROM messages WHERE created_at LIKE ?', (f'{date}%',))
                messages = cursor.fetchone()['count']

            stats.append({
                'date': date,
                'new_users': new_users,
                'messages': messages
            })

        return stats

# Admin instance
admin = AdminManager()
