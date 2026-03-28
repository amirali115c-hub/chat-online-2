"""
Auth blueprint — login, register, guest, logout HTTP routes.
All Socket.IO auth events (login, register) stay in app.py.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='')


def login_required(f):
    """Decorator requiring valid session user_id."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


def guest_required(f):
    """Decorator requiring guest or registered session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id') and not session.get('is_guest'):
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/login')
def login_page():
    return render_template('login.html')


@auth_bp.route('/register')
def register_page():
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_page'))


@auth_bp.route('/welcome')
def welcome_page():
    return render_template('welcome.html')
