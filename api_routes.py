from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import uuid
import re
from database import (
    init_database, get_db, create_user, get_user_by_id, get_user_by_username,
    get_user_by_email, update_user_online_status, search_users,
    create_message, get_messages, create_friend_request, get_friends,
    get_pending_friend_requests, accept_friend_request, reject_friend_request,
    create_room, get_rooms, get_room_by_id, join_room, leave_room,
    get_room_messages, create_room_message, create_notification,
    get_notifications, mark_notification_read, get_stats
)

# Create API blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# JWT Secret (in production, use environment variable)
JWT_SECRET = 'chat-online-jwt-secret-change-in-production'
JWT_ALGORITHM = 'HS256'

# Initialize database
init_database()


# ==================== HELPER FUNCTIONS ====================

def generate_token(user_id, username):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)


def validate_username(username):
    """Validate username format"""
    if len(username) < 3 or len(username) > 50:
        return False
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    return True


def user_to_dict(user):
    """Convert user dict to API response format"""
    return {
        'id': user.get('id'),
        'username': user.get('username'),
        'email': user.get('email'),
        'gender': user.get('gender'),
        'age': user.get('age'),
        'country': user.get('country'),
        'state': user.get('state'),
        'bio': user.get('bio'),
        'avatar': user.get('avatar'),
        'is_online': bool(user.get('is_online')),
        'last_seen': user.get('last_seen'),
        'created_at': user.get('created_at')
    }


# ==================== AUTH ROUTES ====================

@api.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower() if data.get('email') else None
    password = data.get('password', '')
    gender = data.get('gender')
    age = data.get('age')
    country = data.get('country', '')
    state = data.get('state', '')

    # Validation
    errors = []

    if not username:
        errors.append({'field': 'username', 'message': 'Username is required'})
    elif not validate_username(username):
        errors.append({'field': 'username', 'message': 'Username must be 3-50 characters, alphanumeric only'})

    if not password or len(password) < 8:
        errors.append({'field': 'password', 'message': 'Password must be at least 8 characters'})
    elif not re.search(r'[A-Z]', password):
        errors.append({'field': 'password', 'message': 'Password must contain at least one uppercase letter'})
    elif not re.search(r'[a-z]', password):
        errors.append({'field': 'password', 'message': 'Password must contain at least one lowercase letter'})
    elif not re.search(r'[0-9]', password):
        errors.append({'field': 'password', 'message': 'Password must contain at least one number'})

    if email and not validate_email(email):
        errors.append({'field': 'email', 'message': 'Invalid email format'})

    if gender not in ['male', 'female', 'other']:
        errors.append({'field': 'gender', 'message': 'Invalid gender'})

    if age and (int(age) < 18 or int(age) > 100):
        errors.append({'field': 'age', 'message': 'Age must be 18 or older'})

    if errors:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Validation failed',
                'details': errors
            }
        }), 400

    # Check if username exists
    if get_user_by_username(username):
        return jsonify({
            'success': False,
            'error': {
                'code': 'USER_EXISTS',
                'message': 'Username already taken'
            }
        }), 400

    # Check if email exists
    if email and get_user_by_email(email):
        return jsonify({
            'success': False,
            'error': {
                'code': 'EMAIL_EXISTS',
                'message': 'Email already registered'
            }
        }), 400

    # Create user
    password_hash = generate_password_hash(password)
    user_id = create_user(username, email, password_hash, gender, age, country, state)

    # Generate token
    token = generate_token(user_id, username)

    user = get_user_by_id(user_id)

    return jsonify({
        'success': True,
        'data': {
            'user': user_to_dict(user),
            'token': token
        }
    }), 201


@api.route('/auth/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()

    username_or_email = data.get('usernameOrEmail', '').strip()
    password = data.get('password', '')

    if not username_or_email or not password:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_CREDENTIALS',
                'message': 'Username/email and password required'
            }
        }), 401

    # Find user
    user = get_user_by_username(username_or_email)
    if not user:
        # Try email
        user = get_user_by_email(username_or_email.lower())

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_CREDENTIALS',
                'message': 'Invalid username or password'
            }
        }), 401

    # Update online status
    update_user_online_status(user['id'], 1)

    # Generate token
    token = generate_token(user['id'], user['username'])

    return jsonify({
        'success': True,
        'data': {
            'user': user_to_dict(user),
            'token': token
        }
    })


@api.route('/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if token:
        payload = decode_token(token)
        if payload:
            update_user_online_status(payload['user_id'], 0)

    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })


@api.route('/auth/me', methods=['GET'])
def get_current_user():
    """Get current user profile"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Not authenticated'}
        }), 401

    payload = decode_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}
        }), 401

    user = get_user_by_id(payload['user_id'])
    if not user:
        return jsonify({
            'success': False,
            'error': {'code': 'USER_NOT_FOUND', 'message': 'User not found'}
        }), 404

    return jsonify({
        'success': True,
        'data': user_to_dict(user)
    })


# ==================== USER ROUTES ====================

@api.route('/users/search', methods=['GET'])
def search_users_api():
    """Search users by username"""
    query = request.args.get('q', '').strip()
    limit = int(request.args.get('limit', 20))

    if len(query) < 2:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_QUERY', 'message': 'Search query must be at least 2 characters'}
        }), 400

    users = search_users(query, limit)

    return jsonify({
        'success': True,
        'data': [user_to_dict(user) for user in users]
    })


@api.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    user = get_user_by_id(user_id)

    if not user:
        return jsonify({
            'success': False,
            'error': {'code': 'USER_NOT_FOUND', 'message': 'User not found'}
        }), 404

    return jsonify({
        'success': True,
        'data': user_to_dict(user)
    })


# ==================== FRIENDS ROUTES ====================

@api.route('/friends', methods=['GET'])
def get_friends_api():
    """Get user's friends list"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Not authenticated'}
        }), 401

    payload = decode_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}
        }), 401

    friends = get_friends(payload['user_id'])

    return jsonify({
        'success': True,
        'data': [user_to_dict(friend) for friend in friends]
    })


@api.route('/friends/request', methods=['POST'])
def send_friend_request():
    """Send a friend request"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Not authenticated'}
        }), 401

    payload = decode_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}
        }), 401

    data = request.get_json()
    target_username = data.get('username', '').strip()

    if not target_username:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_REQUEST', 'message': 'Username required'}
        }), 400

    user_id = payload['user_id']

    # Find target user
    target_user = get_user_by_username(target_username)
    if not target_user:
        return jsonify({
            'success': False,
            'error': {'code': 'USER_NOT_FOUND', 'message': 'User not found'}
        }), 404

    if target_user['id'] == user_id:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_REQUEST', 'message': 'Cannot add yourself'}
        }), 400

    # Create friend request
    success = create_friend_request(user_id, target_user['id'])

    if not success:
        return jsonify({
            'success': False,
            'error': {'code': 'ALREADY_EXISTS', 'message': 'Friend request already exists'}
        }), 400

    # Create notification
    user = get_user_by_id(user_id)
    create_notification(
        target_user['id'],
        'friend_request',
        'New Friend Request',
        f'{user["username"]} sent you a friend request',
        '/friends'
    )

    return jsonify({
        'success': True,
        'message': 'Friend request sent'
    })


@api.route('/friends/request/accept', methods=['POST'])
def accept_friend_request():
    """Accept a friend request"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Not authenticated'}
        }), 401

    payload = decode_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}
        }), 401

    data = request.get_json()
    requester_id = data.get('user_id')

    if not requester_id:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_REQUEST', 'message': 'User ID required'}
        }), 400

    user_id = payload['user_id']

    # Accept request
    accept_friend_request(user_id, requester_id)

    # Notify requester
    user = get_user_by_id(user_id)
    create_notification(
        requester_id,
        'friend_accepted',
        'Friend Request Accepted',
        f'{user["username"]} accepted your friend request',
        '/friends'
    )

    return jsonify({
        'success': True,
        'message': 'Friend request accepted'
    })


@api.route('/friends/request/reject', methods=['POST'])
def reject_friend_request():
    """Reject a friend request"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Not authenticated'}
        }), 401

    payload = decode_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}
        }), 401

    data = request.get_json()
    requester_id = data.get('user_id')

    if requester_id:
        reject_friend_request(payload['user_id'], requester_id)

    return jsonify({
        'success': True,
        'message': 'Friend request rejected'
    })


@api.route('/friends/requests', methods=['GET'])
def get_friend_requests():
    """Get pending friend requests"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Not authenticated'}
        }), 401

    payload = decode_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}
        }), 401

    requests = get_pending_friend_requests(payload['user_id'])

    requests_list = []
    for req in requests:
        req_dict = user_to_dict(req)
        req_dict['request_id'] = req.get('request_id')
        req_dict['created_at'] = req.get('request_time')
        requests_list.append(req_dict)

    return jsonify({
        'success': True,
        'data': requests_list
    })


# ==================== MESSAGES ROUTES ====================

@api.route('/messages', methods=['GET'])
def get_messages_api():
    """Get user's messages"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Not authenticated'}
        }), 401

    payload = decode_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}
        }), 401

    message_type = request.args.get('type', 'received')
    messages = get_messages(payload['user_id'], message_type)

    return jsonify({
        'success': True,
        'data': messages
    })


@api.route('/messages/send', methods=['POST'])
def send_message_api():
    """Send a direct message"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Not authenticated'}
        }), 401

    payload = decode_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}
        }), 401

    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()

    if not receiver_id or not content:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_REQUEST', 'message': 'Receiver and content required'}
        }), 400

    user_id = payload['user_id']

    # Create message
    message_id = create_message(user_id, receiver_id, content)

    # Create notification
    receiver = get_user_by_id(receiver_id)
    if receiver:
        sender = get_user_by_id(user_id)
        create_notification(
            receiver_id,
            'new_message',
            'New Message',
            f'{sender["username"]} sent you a message',
            '/inbox'
        )

    return jsonify({
        'success': True,
        'data': {'id': message_id, 'content': content}
    }), 201


# ==================== ROOMS ROUTES ====================

@api.route('/rooms', methods=['GET'])
def get_rooms_api():
    """Get all chat rooms"""
    category = request.args.get('category', 'all')
    rooms = get_rooms(category)

    return jsonify({
        'success': True,
        'data': rooms
    })


@api.route('/rooms', methods=['POST'])
def create_room_api():
    """Create a new chat room"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Not authenticated'}
        }), 401

    payload = decode_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}
        }), 401

    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    room_type = data.get('room_type', 'public')
    category = data.get('category', 'general')

    if not name:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_REQUEST', 'message': 'Room name required'}
        }), 400

    room_id = create_room(name, description, room_type, category, payload['user_id'])
    room = get_room_by_id(room_id)

    return jsonify({
        'success': True,
        'data': room
    }), 201


@api.route('/rooms/<room_id>/join', methods=['POST'])
def join_room_api(room_id):
    """Join a chat room"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Not authenticated'}
        }), 401

    payload = decode_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}
        }), 401

    room = get_room_by_id(room_id)
    if not room:
        return jsonify({
            'success': False,
            'error': {'code': 'ROOM_NOT_FOUND', 'message': 'Room not found'}
        }), 404

    success = join_room(room_id, payload['user_id'])

    if not success:
        return jsonify({
            'success': False,
            'error': {'code': 'ALREADY_MEMBER', 'message': 'Already a member'}
        }), 400

    return jsonify({
        'success': True,
        'message': 'Joined room successfully'
    })


@api.route('/rooms/<room_id>/leave', methods=['POST'])
def leave_room_api(room_id):
    """Leave a chat room"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Not authenticated'}
        }), 401

    payload = decode_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}
        }), 401

    leave_room(room_id, payload['user_id'])

    return jsonify({
        'success': True,
        'message': 'Left room successfully'
    })


@api.route('/rooms/<room_id>/messages', methods=['GET'])
def get_room_messages_api(room_id):
    """Get room messages"""
    limit = int(request.args.get('limit', 50))
    messages = get_room_messages(room_id, limit)

    return jsonify({
        'success': True,
        'data': messages
    })


# ==================== NOTIFICATIONS ROUTES ====================

@api.route('/notifications', methods=['GET'])
def get_notifications_api():
    """Get user notifications"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Not authenticated'}
        }), 401

    payload = decode_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}
        }), 401

    limit = int(request.args.get('limit', 20))
    notifications = get_notifications(payload['user_id'], limit)

    return jsonify({
        'success': True,
        'data': notifications
    })


@api.route('/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read_api(notification_id):
    """Mark notification as read"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Not authenticated'}
        }), 401

    payload = decode_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}
        }), 401

    mark_notification_read(notification_id, payload['user_id'])

    return jsonify({
        'success': True,
        'message': 'Notification marked as read'
    })


# ==================== STATS ROUTES ====================

@api.route('/stats', methods=['GET'])
def get_stats_api():
    """Get platform statistics"""
    stats = get_stats()
    return jsonify({
        'success': True,
        'data': stats
    })
