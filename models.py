"""
Models Layer - Wraps database.py functions with proper error handling
Returns (success: bool, data: Any) tuples for all operations
"""
from typing import Any, Tuple, Optional
import logging
import hashlib

from database import (
    create_user as db_create_user,
    get_user_by_id as db_get_user_by_id,
    get_user_by_username as db_get_user_by_username,
    get_user_by_email as db_get_user_by_email,
    update_user_online_status as db_update_user_online_status,
    create_message as db_create_message,
    create_friend_request as db_create_friend_request,
    get_friends as db_get_friends,
    get_pending_friend_requests as db_get_pending_friend_requests,
    accept_friend_request as db_accept_friend_request,
    search_users as db_search_users,
)

logger = logging.getLogger('chat_online')


def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == password_hash


def create_user(
    username: str,
    email: str,
    password: str,
    gender: str = None,
    age: int = None,
    country: str = None,
    state: str = None
) -> Tuple[bool, Any]:
    """
    Create a new user in the database.
    Returns: (success: bool, data: user_id or error_message)
    """
    try:
        password_hash = hash_password(password)
        user_id = db_create_user(
            username=username,
            email=email,
            password_hash=password_hash,
            gender=gender,
            age=age,
            country=country,
            state=state
        )
        return (True, user_id)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return (False, str(e))


def get_user_by_id(user_id: str) -> Tuple[bool, Any]:
    """Get user by ID. Returns (success, user_dict or error)"""
    try:
        user = db_get_user_by_id(user_id)
        if user is None:
            return (False, "User not found")
        # Don't return password_hash
        if 'password_hash' in user:
            del user['password_hash']
        return (True, user)
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return (False, str(e))


def get_user_by_username(username: str) -> Tuple[bool, Any]:
    """Get user by username. Returns (success, user_dict or error)"""
    try:
        user = db_get_user_by_username(username)
        if user is None:
            return (False, "User not found")
        # Don't return password_hash
        if 'password_hash' in user:
            del user['password_hash']
        return (True, user)
    except Exception as e:
        logger.error(f"Error getting user by username: {e}")
        return (False, str(e))


def get_user_by_email(email: str) -> Tuple[bool, Any]:
    """Get user by email. Returns (success, user_dict or error)"""
    try:
        user = db_get_user_by_email(email)
        if user is None:
            return (False, "User not found")
        # Don't return password_hash
        if 'password_hash' in user:
            del user['password_hash']
        return (True, user)
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return (False, str(e))


def authenticate_user(username: str, password: str) -> Tuple[bool, Any]:
    """
    Authenticate a user by username and password.
    Returns: (success: bool, data: user_dict or error_message)
    """
    try:
        # Try to find user by username first
        success, result = get_user_by_username(username)
        if not success:
            # Try by email
            success, result = get_user_by_email(username)
            if not success:
                return (False, "User not found")
        
        user = result
        if 'password_hash' not in user:
            return (False, "User has no password set")
        
        if verify_password(password, user['password_hash']):
            # Don't return password_hash
            if 'password_hash' in user:
                del user['password_hash']
            return (True, user)
        else:
            return (False, "Invalid password")
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return (False, str(e))


def update_user_online_status(user_id: str, is_online: int) -> Tuple[bool, Any]:
    """Update user's online status. Returns (success, None or error)"""
    try:
        db_update_user_online_status(user_id, is_online)
        return (True, None)
    except Exception as e:
        logger.error(f"Error updating user online status: {e}")
        return (False, str(e))


def create_message(
    sender_id: str,
    receiver_id: str,
    content: str,
    room_id: str = None
) -> Tuple[bool, Any]:
    """Create a new message. Returns (success, message_id or error)"""
    try:
        message_id = db_create_message(sender_id, receiver_id, content, room_id)
        return (True, message_id)
    except Exception as e:
        logger.error(f"Error creating message: {e}")
        return (False, str(e))


def create_friend_request(user_id: str, friend_id: str) -> Tuple[bool, Any]:
    """Create a friend request. Returns (success, True or error_message)"""
    try:
        result = db_create_friend_request(user_id, friend_id)
        if result:
            return (True, True)
        return (False, "Failed to create friend request (possibly already exists)")
    except Exception as e:
        logger.error(f"Error creating friend request: {e}")
        return (False, str(e))


def get_friends(user_id: str) -> Tuple[bool, Any]:
    """Get user's friends list. Returns (success, friends_list or error)"""
    try:
        friends = db_get_friends(user_id)
        # Clean up password_hash from each friend
        for friend in friends:
            if 'password_hash' in friend:
                del friend['password_hash']
        return (True, friends)
    except Exception as e:
        logger.error(f"Error getting friends: {e}")
        return (False, str(e))


def get_pending_friend_requests(user_id: str) -> Tuple[bool, Any]:
    """Get pending friend requests. Returns (success, requests_list or error)"""
    try:
        requests = db_get_pending_friend_requests(user_id)
        # Clean up password_hash from each requester
        for req in requests:
            if 'password_hash' in req:
                del req['password_hash']
        return (True, requests)
    except Exception as e:
        logger.error(f"Error getting pending friend requests: {e}")
        return (False, str(e))


def accept_friend_request(user_id: str, requester_id: str) -> Tuple[bool, Any]:
    """Accept a friend request. Returns (success, None or error)"""
    try:
        db_accept_friend_request(user_id, requester_id)
        return (True, None)
    except Exception as e:
        logger.error(f"Error accepting friend request: {e}")
        return (False, str(e))


def check_username_exists(username: str) -> Tuple[bool, Any]:
    """
    Check if a username already exists in the database.
    Returns: (success: bool, exists: bool)
    """
    try:
        user = db_get_user_by_username(username)
        return (True, user is not None)
    except Exception as e:
        logger.error(f"Error checking username: {e}")
        return (False, str(e))


def search_users(query: str, limit: int = 20) -> Tuple[bool, Any]:
    """Search users by username. Returns (success, users_list or error)"""
    try:
        users = db_search_users(query, limit)
        # Clean up password_hash from each user
        for user in users:
            if 'password_hash' in user:
                del user['password_hash']
        return (True, users)
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        return (False, str(e))
