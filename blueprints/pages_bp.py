"""
Pages blueprint — public and feature page routes.
"""
from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def index():
    from app import honeypot_tokens, generate_honeypot_token
    import time
    honeypot_token = generate_honeypot_token()
    session['honeypot_token'] = honeypot_token
    session['session_start'] = time.time()
    from app import _add_honeypot
    _add_honeypot(honeypot_token)
    return render_template('index.html')


@pages_bp.route('/home')
def home():
    return render_template('index.html')


@pages_bp.route('/chat')
def main_chat():
    return render_template('main_chat.html')


@pages_bp.route('/chat-rooms')
def chat_rooms():
    return render_template('chat_rooms.html')


@pages_bp.route('/random-chat')
def random_chat():
    return render_template('random_chat.html')


@pages_bp.route('/dating-channels')
def dating_channels():
    return render_template('dating_channels.html')


@pages_bp.route('/about')
def about():
    return render_template('about.html')


@pages_bp.route('/blog/<slug>')
def blog_article(slug):
    from app import get_blog_post
    post = get_blog_post(slug)
    if post:
        return render_template('blog_article.html', post=post, page_title=post['title'])
    from flask import abort
    abort(404)


@pages_bp.route('/faq')
def faq():
    return render_template('faq.html')


@pages_bp.route('/terms')
def terms():
    return render_template('terms.html')


@pages_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')


@pages_bp.route('/safety')
def safety():
    return render_template('safety.html')


@pages_bp.route('/contact')
def contact():
    return render_template('contact.html')


@pages_bp.route('/profile')
def profile_page():
    return render_template('profile.html')


@pages_bp.route('/friends')
def friends_page():
    return render_template('friends.html')


@pages_bp.route('/inbox')
def inbox_page():
    return render_template('inbox.html')


@pages_bp.route('/history')
def history_page():
    return render_template('history.html')


@pages_bp.route('/settings')
def settings_page():
    return render_template('settings.html')


@pages_bp.route('/offline')
def offline_page():
    return render_template('offline.html')


# Error handlers
@pages_bp.errorhandler(404)
def not_found(error):
    from flask import render_template
    return render_template('error.html',
                           error_code=404,
                           error_message='Page Not Found',
                           error_description='The page you are looking for does not exist.'), 404


@pages_bp.errorhandler(500)
def internal_error(error):
    from flask import render_template
    return render_template('error.html',
                           error_code=500,
                           error_message='Internal Server Error',
                           error_description='Something went wrong on our end. Please try again later.'), 500


@pages_bp.errorhandler(403)
def forbidden(error):
    from flask import render_template
    return render_template('error.html',
                           error_code=403,
                           error_message='Forbidden',
                           error_description='You do not have permission to access this resource.'), 403


@pages_bp.errorhandler(400)
def bad_request(error):
    from flask import render_template
    return render_template('error.html',
                           error_code=400,
                           error_message='Bad Request',
                           error_description='The request could not be understood by the server.'), 400
