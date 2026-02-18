import json
import os
import re
import time
import uuid
import hashlib
import threading
import logging
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, session, jsonify, redirect, url_for, send_from_directory, g
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
from collections import defaultdict
from config import get_config

# Load configuration
config = get_config()

# Setup logging - FILE ONLY for production performance
os.makedirs('logs', exist_ok=True)
file_handler = RotatingFileHandler(
    config.LOG_FILE,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=10,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO if not config.DEBUG else logging.DEBUG)

# Configure logger - NO console handler for performance
logger = logging.getLogger('chat_online')
logger.setLevel(logging.INFO if not config.DEBUG else logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Log application startup ONLY in debug mode
if config.DEBUG:
    print("=" * 60)
    print("Chat Online Application Starting")
    print("=" * 60)

# Markdown support
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("Markdown module not available - install with: pip install markdown")

# Configuration
BLOG_CONTENT_DIR = 'content/blog'
UPLOAD_DIR = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Ensure directories exist
os.makedirs(BLOG_CONTENT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')
    return text

def parse_frontmatter(content):
    """Parse YAML frontmatter and content from markdown file"""
    if content.startswith('---'):
        parts = content[4:].split('---', 1)
        if len(parts) == 2:
            frontmatter = parts[0].strip()
            body = parts[1].strip()
            
            data = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip()] = value.strip()
            
            return data, body
    return {}, content

def generate_frontmatter(data, body):
    """Generate markdown with frontmatter"""
    lines = ['---']
    for key, value in data.items():
        lines.append(f'{key}: {value}')
    lines.append('---')
    lines.append('')
    lines.append(body)
    return '\n'.join(lines)

def get_blog_posts():
    """Get all blog posts from content directory"""
    posts = []
    
    if not os.path.exists(BLOG_CONTENT_DIR):
        return posts
    
    for filename in os.listdir(BLOG_CONTENT_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(BLOG_CONTENT_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                data, body = parse_frontmatter(content)
                
                # Convert markdown to HTML if available
                html_content = body
                if MARKDOWN_AVAILABLE:
                    md = markdown.Markdown(extensions=['tables', 'fenced_code'])
                    html_content = md.convert(body)
                
                # Generate excerpt from content
                excerpt = data.get('excerpt', '')
                if not excerpt and body:
                    excerpt = body[:200] + '...' if len(body) > 200 else body
                
                # Generate color and icon based on category
                colors = {
                    'Safety': 'linear-gradient(135deg, #0EA5E9, #06B6D4)',
                    'Community': 'linear-gradient(135deg, #8B5CF6, #7C3AED)',
                    'Tips': 'linear-gradient(135deg, #10B981, #059669)',
                    'Random Chat': 'linear-gradient(135deg, #F59E0B, #D97706)',
                    'Global': 'linear-gradient(135deg, #6366F1, #4F46E5)',
                    'News': 'linear-gradient(135deg, #EC4899, #DB2777)'
                }
                icons = {
                    'Safety': 'fa-shield-alt',
                    'Community': 'fa-user-friends',
                    'Tips': 'fa-lightbulb',
                    'Random Chat': 'fa-dice',
                    'Global': 'fa-globe',
                    'News': 'fa-newspaper'
                }
                
                posts.append({
                    'slug': data.get('slug', filename[:-3]),
                    'title': data.get('title', 'Untitled'),
                    'meta_title': data.get('meta_title', ''),
                    'meta_description': data.get('meta_description', ''),
                    'featured_image': data.get('featured_image', ''),
                    'category': data.get('category', 'Tips'),
                    'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                    'author': data.get('author', 'Admin'),
                    'excerpt': excerpt,
                    'content': body,
                    'html_content': html_content,
                    'color': colors.get(data.get('category', 'Tips'), 'linear-gradient(135deg, #8B5CF6, #7C3AED)'),
                    'icon': icons.get(data.get('category', 'Tips'), 'fa-newspaper')
                })
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    # Sort by date descending
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

def get_blog_post(slug):
    """Get a single blog post by slug"""
    posts = get_blog_posts()
    for post in posts:
        if post['slug'] == slug:
            return post
    return None

def save_blog_post(title, slug, content, category, date, excerpt, meta_title, meta_description, featured_image=None):
    """Save a blog post"""
    # Ensure slug
    if not slug:
        slug = slugify(title)
    
    # Check if post exists
    filepath = os.path.join(BLOG_CONTENT_DIR, f'{slug}.md')
    existing_post = None
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        existing_data, _ = parse_frontmatter(existing_content)
        existing_post = existing_data
    
    # Preserve existing featured_image if not uploading new one
    current_image = featured_image
    if not current_image and existing_post:
        current_image = existing_post.get('featured_image', '')
    
    # Build frontmatter data
    data = {
        'title': title,
        'slug': slug,
        'category': category,
        'date': date,
        'author': 'Admin',
        'excerpt': excerpt,
        'meta_title': meta_title,
        'meta_description': meta_description,
        'featured_image': current_image
    }
    
    # Generate markdown with frontmatter
    markdown_content = generate_frontmatter(data, content)
    
    # Save file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return slug

def delete_blog_post(slug):
    """Delete a blog post"""
    filepath = os.path.join(BLOG_CONTENT_DIR, f'{slug}.md')
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def get_uploaded_images():
    """Get list of uploaded images"""
    images = []
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            if allowed_file(filename):
                filepath = os.path.join(UPLOAD_DIR, filename)
                images.append({
                    'filename': filename,
                    'url': f'/static/uploads/{filename}',
                    'size': os.path.getsize(filepath),
                    'date': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d')
                })
    return sorted(images, key=lambda x: x['date'], reverse=True)

def handle_file_upload(file):
    """Handle image upload and return URL"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        name, ext = os.path.splitext(filename)
        filename = f'{name}_{int(time.time())}{ext}'
        filepath = os.path.join(UPLOAD_DIR, filename)
        file.save(filepath)
        return f'/static/uploads/{filename}'
    return None
import uuid
import time
import hashlib
import re
import os
from collections import defaultdict
from config import Config
from database import init_database
from api_routes import api
from csrf import generate_csrf_token, validate_csrf_token

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Initialize Sentry for error tracking (optional - set SENTRY_DSN env var to enable)
SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.socketio import SocketIOIntegration
        
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[FlaskIntegration(), SocketIOIntegration()],
            traces_sample_rate=0.1,
            send_default_pii=False
        )
        logger.info("Sentry error tracking initialized")
    except ImportError:
        logger.warning("Sentry SDK not installed - error tracking disabled")

# Add CSRF token generator to Jinja context
app.jinja_env.globals['csrf_token'] = generate_csrf_token

# Health check endpoint for Koyeb (MUST be before anything else)
@app.route('/health')
def health():
    return {'status': 'ok'}, 200

# Initialize database (with error handling for Koyeb)
try:
    init_database()
    print("Database initialized successfully")
except Exception as e:
    print(f"Database initialization warning: {e}")
    print("App will continue - database will initialize when needed")

# Register API blueprint
app.register_blueprint(api)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ==================== REAL-TIME USER TRACKING ====================

# Track active Socket.IO connections
# Format: {sid: {user_id, username, gender, country, current_room, connected_at}}
active_connections = {}

# Global room for broadcasting user counts
GLOBAL_ONLINE_ROOM = "global_online_users"

# ==================== ANTI-BOT SECURITY SYSTEM ====================

# Track connection attempts per IP
ip_connections = defaultdict(list)
ip_message_counts = defaultdict(list)
ip_request_counts = defaultdict(list)

# Maximum connections per IP
MAX_CONNECTIONS_PER_IP = 3
MAX_MESSAGES_PER_MINUTE = 20
MAX_REQUESTS_PER_MINUTE = 30

# Bot detection patterns
BOT_USER_AGENTS = [
    'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget',
    'python', 'java', 'node', 'ruby', 'go', 'rust',
    'headless', 'puppeteer', 'selenium', 'phantom',
    'httpclient', 'requests', 'urllib', 'httpx'
]

# Known proxy/ VPN IP ranges (simplified - in production use a service)
SUSPICIOUS_HEADERS = [
    'x-forwarded-for', 'x-real-ip', 'cf-connecting-ip',
    'true-client-ip', 'x-cluster-client-ip'
]

# Rate limiting decorator
def check_rate_limit(ip, action='message'):
    """Check if IP has exceeded rate limits"""
    current_time = time.time()

    if action == 'message':
        # Clean old entries
        ip_message_counts[ip] = [t for t in ip_message_counts[ip] if current_time - t < 60]
        if len(ip_message_counts[ip]) >= MAX_MESSAGES_PER_MINUTE:
            return False
        ip_message_counts[ip].append(current_time)
    elif action == 'request':
        ip_request_counts[ip] = [t for t in ip_request_counts[ip] if current_time - t < 60]
        if len(ip_request_counts[ip]) >= MAX_REQUESTS_PER_MINUTE:
            return False
        ip_request_counts[ip].append(current_time)

    return True

def get_client_ip():
    """Get real client IP address"""
    # Check common proxy headers
    for header in SUSPICIOUS_HEADERS:
        if request.headers.get(header):
            return request.headers.get(header).split(',')[0].strip()

    return request.remote_addr

def is_bot_request():
    """Check if request appears to be from a bot"""
    user_agent = request.headers.get('User-Agent', '').lower()

    # Check for bot user agents
    for bot_ua in BOT_USER_AGENTS:
        if bot_ua in user_agent:
            return True

    # Check for missing user agent
    if not user_agent or user_agent == '':
        return True

    return False

def validate_session():
    """Validate user session for authenticity"""
    # Check if session exists and has required data
    if 'session_start' not in session:
        # For guest users, check if they have guest verification
        if session.get('is_guest') and session.get('age_verified'):
            return True
        return False

    # Session should be at least 2 seconds old (prevents instant bot registration)
    session_age = time.time() - session.get('session_start', 0)
    if session_age < 2:
        return False

    # Check for valid session fingerprint
    if 'fingerprint' not in session:
        return False

    return True

def generate_honeypot_token():
    """Generate a honeypot token"""
    return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]

# Store active users and queues
users = {}
registered_users = {}
used_usernames = set()

# Friends system - {user_id: [friend_id1, friend_id2, ...]}
friends = {}

# Friend requests - {user_id: [request_from_user_id1, request_from_user_id2, ...]}
friend_requests = {}

# Honeypot tokens storage
honeypot_tokens = set()

# Waiting queues by gender preference
waiting_queues = {
    'male': {'any': [], 'opposite': [], 'same': []},
    'female': {'any': [], 'opposite': [], 'same': []}
}

def generate_user_id():
    return str(uuid.uuid4())

def get_partner_gender(user_gender, preference):
    if preference == 'any':
        return None
    elif preference == 'opposite':
        return 'female' if user_gender == 'male' else 'male'
    elif preference == 'same':
        return user_gender
    return None

def find_partner(user_id, user_gender, partner_pref):
    partner_gender = get_partner_gender(user_gender, partner_pref)

    if partner_pref == 'any':
        for pref in ['any', 'same', 'opposite']:
            queue = waiting_queues[user_gender][pref]
            if queue:
                return queue.pop(0)
    elif partner_pref == 'opposite':
        opposite_gender = 'female' if user_gender == 'male' else 'male'
        for pref in ['any', 'opposite']:
            queue = waiting_queues[opposite_gender][pref]
            if queue:
                return queue.pop(0)
    elif partner_pref == 'same':
        for pref in ['any', 'same']:
            queue = waiting_queues[user_gender][pref]
            if queue:
                return queue.pop(0)

    return None

def add_to_queue(user_id, gender, preference):
    waiting_queues[gender][preference].append(user_id)

def remove_from_queue(user_id):
    for gender in waiting_queues:
        for pref in waiting_queues[gender]:
            if user_id in waiting_queues[gender][pref]:
                waiting_queues[gender][pref].remove(user_id)

def create_chat_room(user1_id, user2_id):
    room_id = str(uuid.uuid4())
    return room_id

# ==================== ROUTES ====================

@app.route('/')
def index():
    # Generate honeypot token for this session
    honeypot_token = generate_honeypot_token()
    session['honeypot_token'] = honeypot_token
    session['session_start'] = time.time()
    honeypot_tokens.add(honeypot_token)

    return render_template('index.html')

@app.route('/guest-login', methods=['POST'])
def guest_login():
    """Handle guest form submission"""
    username = request.form.get('username', '').strip()
    gender = request.form.get('gender', '')
    age = request.form.get('age', '')
    country = request.form.get('country', '')
    state = request.form.get('state', '')
    
    if not username or not gender or not age or not country:
        return render_template('index.html')
    
    # Store in session
    session['guest_username'] = username
    session['guest_gender'] = gender
    session['guest_age'] = age
    session['guest_country'] = country
    session['guest_state'] = state or ''
    session['is_guest'] = True
    session['age_verified'] = True
    session['agreed_at'] = time.time()
    
    # Redirect with verified parameter
    return app.redirect('/welcome?verified=1', code=302)

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/api/verify-human', methods=['POST'])
def verify_human():
    """Verify human verification challenge"""
    client_ip = get_client_ip()

    # Rate limit
    if not check_rate_limit(client_ip, 'request'):
        return jsonify({'success': False, 'error': 'Too many requests'})

    data = request.get_json()
    token = data.get('token', '')
    challenge = data.get('challenge', '')

    # Validate honeypot
    if token in honeypot_tokens:
        honeypot_tokens.discard(token)
        session['human_verified'] = True
        session['fingerprint'] = hashlib.md5(client_ip.encode()).hexdigest()
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Verification failed'})

@app.route('/api/check-rate-limit', methods=['GET'])
def check_rate():
    """Check if IP is rate limited"""
    client_ip = get_client_ip()

    if not check_rate_limit(client_ip, 'request'):
        return jsonify({'limited': True, 'retry_after': 60})

    return jsonify({'limited': False})

# ==================== SOCKET HANDLERS ====================

@socketio.on('connect')
def handle_connect():
    client_ip = get_client_ip()
    
    # Check if blocked
    if is_ip_blocked(client_ip):
        logger.warning(f"Blocked IP attempted connection: {client_ip}")
        emit('error', {'message': 'Access denied'})
        return False
    
    # Check if bot
    if is_bot_request():
        logger.info(f"Bot blocked: {client_ip}")
        emit('error', {'message': 'Access denied'})
        return False

    # Rate limit connections
    current_time = time.time()
    ip_connections[client_ip] = [t for t in ip_connections[client_ip] if current_time - t < 60]

    if len(ip_connections[client_ip]) >= MAX_CONNECTIONS_PER_IP:
        logger.warning(f"Connection limit exceeded from {client_ip}")
        emit('error', {'message': 'Too many connections from your IP'})
        return False

    ip_connections[client_ip].append(current_time)

    # Validate session - allow guests with age_verified
    if not validate_session():
        emit('error', {'message': 'Invalid session. Please refresh the page.'})
        return False

    user_id = generate_user_id()
    
    # Check if guest user
    is_guest = session.get('is_guest', False)
    username = session.get('guest_username', 'Guest')
    gender = session.get('guest_gender', None)
    country = session.get('guest_country', '')
    
    # Store session data
    session['user_id'] = user_id
    session['username'] = username
    session['gender'] = gender
    session['country'] = country
    
    users[user_id] = {
        'gender': gender,
        'partner_pref': None,
        'partner_id': None,
        'room': None,
        'username': username,
        'country': country,
        'is_guest': is_guest,
        'connected_at': time.time(),
        'ip': client_ip,
        'messages_sent': 0,
        'last_message_time': 0
    }
    
    # Track active connection for real-time user counting
    active_connections[request.sid] = {
        'user_id': user_id,
        'session_id': session.sid,
        'username': username,
        'gender': gender,
        'country': country,
        'is_guest': is_guest,
        'current_room': 'lobby',
        'connected_at': current_time,
        'last_ping': current_time
    }
    
    # Join global online users room for broadcasting
    join_room(GLOBAL_ONLINE_ROOM)
    
    # Broadcast updated online count to all clients
    socketio.emit('online_count_update', {
        'total_online': len(active_connections)
    }, room=GLOBAL_ONLINE_ROOM)
    
    # Only log in debug mode
    if config.DEBUG:
        logger.info(f"User connected: {username} (ID: {user_id}) from {client_ip}")
    
    emit('connected', {'user_id': user_id, 'username': username, 'gender': gender, 'is_guest': is_guest})

def cleanup_stale_connections():
    """Remove connections that haven't pinged in 5 minutes"""
    current_time = time.time()
    stale_threshold = 300  # 5 minutes
    
    stale_sids = []
    for sid, conn in active_connections.items():
        last_ping = conn.get('last_ping', conn.get('connected_at', 0))
        if current_time - last_ping > stale_threshold:
            stale_sids.append(sid)
    
    for sid in stale_sids:
        if sid in active_connections:
            del active_connections[sid]
        if sid in users:
            user_id = active_connections.get(sid, {}).get('user_id')
            if user_id and user_id in users:
                del users[user_id]
    
    return len(stale_sids)

# Run cleanup every 5 minutes - reduced logging
import threading
def run_cleanup():
    while True:
        time.sleep(300)  # 5 minutes
        try:
            cleaned = cleanup_stale_connections()
            if cleaned > 0 and config.DEBUG:
                print(f"Cleaned up {cleaned} stale connections")
        except Exception as e:
            if config.DEBUG:
                print(f"Cleanup error: {e}")

cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
cleanup_thread.start()

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    if user_id and user_id in users:
        user = users[user_id]

        if user.get('partner_id'):
            partner_id = user['partner_id']
            if partner_id in users:
                emit('partner_disconnected', room=user['room'], broadcast=True)

            if partner_id in users:
                users[partner_id]['partner_id'] = None
                users[partner_id]['room'] = None

        remove_from_queue(user_id)
        del users[user_id]

    # Remove from active connections
    if request.sid in active_connections:
        del active_connections[request.sid]
    
    # Broadcast updated online count
    socketio.emit('online_count_update', {
        'total_online': len(active_connections)
    }, room=GLOBAL_ONLINE_ROOM)

    print(f'User {user_id} disconnected')

# ============ REAL-TIME USER TRACKING EVENTS ============

@socketio.on('update_user_profile')
def handle_update_profile(data):
    """Update user profile info for tracking"""
    if request.sid in active_connections:
        active_connections[request.sid].update({
            'username': data.get('username'),
            'gender': data.get('gender'),
            'country': data.get('country')
        })

@socketio.on('ping')
def handle_ping():
    """Update user's last ping timestamp"""
    if request.sid in active_connections:
        active_connections[request.sid]['last_ping'] = time.time()
        emit('pong', {'status': 'ok'})

@socketio.on('join_room_tracking')
def handle_join_room_tracking(data):
    """Track when user joins a room"""
    room_id = data.get('room_id', 'lobby')
    
    if request.sid in active_connections:
        active_connections[request.sid]['current_room'] = room_id
    
    # Broadcast room user count
    room_users = [c for c in active_connections.values() if c.get('current_room') == room_id]
    socketio.emit('room_count_update', {
        'room_id': room_id,
        'count': len(room_users)
    }, room=GLOBAL_ONLINE_ROOM)

@socketio.on('leave_room_tracking')
def handle_leave_room_tracking(data):
    """Track when user leaves a room"""
    room_id = data.get('room_id', 'lobby')
    
    if request.sid in active_connections:
        active_connections[request.sid]['current_room'] = 'lobby'
    
    # Broadcast room user count
    room_users = [c for c in active_connections.values() if c.get('current_room') == room_id]
    socketio.emit('room_count_update', {
        'room_id': room_id,
        'count': len(room_users)
    }, room=GLOBAL_ONLINE_ROOM)

@socketio.on('request_online_count')
def handle_request_online_count():
    """Send current online count to requesting client"""
    emit('online_count_update', {
        'total_online': len(active_connections)
    })

@socketio.on('verify_human')
def handle_verify_human(data):
    """Handle human verification"""
    token = data.get('token', '')

    if token in honeypot_tokens:
        honeypot_tokens.discard(token)
        session['human_verified'] = True
        emit('verification_success')
    else:
        emit('verification_failed')

@socketio.on('check_username')
def handle_check_username(data):
    username = data.get('username', '').strip().lower()

    # Basic validation
    if not username or len(username) < 3 or len(username) > 20:
        emit('username_error', {'message': 'Username must be 3-20 characters'})
        return

    # Check for bot-like usernames
    if re.match(r'^[0-9]+$', username):
        emit('username_error', {'message': 'Username must contain letters'})
        return

    if username in [u['username'].lower() for u in registered_users.values()]:
        emit('username_taken', {'username': username})
        return

    if username in used_usernames:
        emit('username_taken', {'username': username})
        return

    emit('username_available', {'username': username})

@socketio.on('login')
def handle_login(data):
    client_ip = get_client_ip()

    # Rate limit
    if not check_rate_limit(client_ip, 'request'):
        emit('login_error', {'message': 'Too many attempts. Please wait.'})
        return

    username = data.get('username', '').strip()

    if not username:
        emit('login_error', {'message': 'Please enter username'})
        return

    user_found = None
    for uid, user_data in registered_users.items():
        if user_data['username'].lower() == username.lower():
            user_found = user_data
            user_found['id'] = uid
            break

    if not user_found:
        emit('login_error', {'message': 'User not found. Please register first.'})
        return

    session['user_id'] = user_found['id']
    users[user_found['id']].update({
        'username': user_found['username'],
        'gender': user_found['gender'],
        'age': user_found.get('age'),
        'country': user_found.get('country'),
        'state': user_found.get('state'),
        'is_registered': True
    })

    emit('login_success', {
        'user': {
            'username': user_found['username'],
            'gender': user_found['gender'],
            'age': user_found.get('age'),
            'country': user_found.get('country'),
            'state': user_found.get('state')
        }
    })

@socketio.on('register')
def handle_register(data):
    client_ip = get_client_ip()

    # Rate limit
    if not check_rate_limit(client_ip, 'request'):
        emit('register_error', {'message': 'Too many attempts. Please wait.'})
        return

    username = data.get('username', '').strip()
    gender = data.get('gender')
    age = data.get('age')
    country = data.get('country')
    state = data.get('state', '')

    # Validate all fields
    if not username or not gender or not age or not country:
        emit('validation_error', {'message': 'All fields are required'})
        return

    # Validate username
    if len(username) < 3 or len(username) > 20:
        emit('register_error', {'message': 'Username must be 3-20 characters'})
        return

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        emit('register_error', {'message': 'Username can only contain letters, numbers, and underscores'})
        return

    # Check if username exists
    if username.lower() in [u['username'].lower() for u in registered_users.values()]:
        emit('register_error', {'message': 'Username already exists'})
        return

    user_id = generate_user_id()
    registered_users[user_id] = {
        'username': username,
        'gender': gender,
        'age': age,
        'country': country,
        'state': state,
        'created_at': time.time(),
        'ip': client_ip
    }

    session['user_id'] = user_id
    users[user_id].update({
        'username': username,
        'gender': gender,
        'age': age,
        'country': country,
        'state': state,
        'is_registered': True
    })

    emit('register_success', {
        'user': {
            'username': username,
            'gender': gender,
            'age': age,
            'country': country,
            'state': state
        }
    })

@socketio.on('find_partner')
def handle_find_partner(data):
    user_id = session.get('user_id')
    if not user_id or user_id not in users:
        emit('error', {'message': 'Not connected properly'})
        return

    username = data.get('username')
    gender = data.get('gender')
    partner_pref = data.get('partner_pref')
    age = data.get('age')
    country = data.get('country')
    state = data.get('state', '')
    is_guest = data.get('is_guest', True)

    if not gender or not partner_pref:
        emit('error', {'message': 'Please select gender and preference'})
        return

    users[user_id]['username'] = username
    users[user_id]['gender'] = gender
    users[user_id]['partner_pref'] = partner_pref
    users[user_id]['age'] = age
    users[user_id]['country'] = country
    users[user_id]['state'] = state

    if is_guest:
        used_usernames.add(username.lower())

    remove_from_queue(user_id)

    partner_id = find_partner(user_id, gender, partner_pref)

    if partner_id and partner_id in users:
        room_id = create_chat_room(user_id, partner_id)

        users[user_id]['partner_id'] = partner_id
        users[user_id]['room'] = room_id

        users[partner_id]['partner_id'] = user_id
        users[partner_id]['room'] = room_id

        join_room(room_id)

        partner = users[partner_id]
        partner_name = partner.get('username', 'Stranger')
        partner_info = ''
        if partner.get('country'):
            country_name = Config.COUNTRIES.get(partner['country'], partner['country'])
            partner_info = f"{partner.get('age', '')} | {country_name}"
            if partner.get('state'):
                partner_info += f", {partner['state']}"

        user_info = f"{age} | {Config.COUNTRIES.get(country, country)}"
        if state:
            user_info += f", {state}"

        emit('partner_found', {
            'room': room_id,
            'partner_gender': users[partner_id]['gender'],
            'partner_name': partner_name,
            'partner_info': partner_info
        })

        emit('partner_found', {
            'room': room_id,
            'partner_gender': gender,
            'partner_name': username,
            'partner_info': user_info
        }, room=room_id)

    else:
        add_to_queue(user_id, gender, partner_pref)
        emit('waiting', {'message': 'Looking for a stranger to chat with...'})

@socketio.on('send_message')
def handle_message(data):
    user_id = session.get('user_id')
    client_ip = get_client_ip()

    if not user_id or user_id not in users:
        emit('error', {'message': 'Not connected properly'})
        return

    # Rate limit messages
    if not check_rate_limit(client_ip, 'message'):
        emit('error', {'message': 'You are sending messages too fast. Please slow down.'})
        return

    user = users[user_id]
    if not user.get('room') or not user.get('partner_id'):
        emit('error', {'message': 'No active chat'})
        return

    message = data.get('message', '').strip()
    if not message:
        return

    # Message length limit
    if len(message) > Config.MAX_MESSAGE_LENGTH:
        message = message[:Config.MAX_MESSAGE_LENGTH]

    # Track message count
    user['messages_sent'] += 1
    user['last_message_time'] = time.time()

    # Block if too many messages
    if user['messages_sent'] > 100:
        emit('error', {'message': 'Message limit reached. Please start a new chat.'})
        return

    emit('new_message', {
        'message': message,
        'sender': 'you',
        'timestamp': time.time()
    }, room=user['room'])

    emit('new_message', {
        'message': message,
        'sender': 'partner',
        'timestamp': time.time()
    }, room=user['room'])
    
    logger.info(f"Message sent by {username} to room {user['room']}")

@socketio.on('typing')
def handle_typing(data):
    user_id = session.get('user_id')
    if not user_id or user_id not in users:
        return

    user = users[user_id]
    if user.get('room'):
        emit('partner_typing', {'is_typing': data.get('is_typing', False)}, room=user['room'])

@socketio.on('next_person')
def handle_next_person():
    user_id = session.get('user_id')
    if not user_id or user_id not in users:
        emit('error', {'message': 'Not connected properly'})
        return

    user = users[user_id]

    if user.get('room'):
        leave_room(user['room'])
        emit('chat_ended', {'message': 'You left the chat'}, room=user['room'])

        if user.get('partner_id') and user['partner_id'] in users:
            partner = users[user['partner_id']]
            if partner.get('room') == user['room']:
                emit('partner_left', room=user['room'])

    user['partner_id'] = None
    user['room'] = None
    user['messages_sent'] = 0

    gender = user.get('gender')
    partner_pref = user.get('partner_pref')

    if gender and partner_pref:
        partner_id = find_partner(user_id, gender, partner_pref)

        if partner_id and partner_id in users:
            room_id = create_chat_room(user_id, partner_id)

            users[user_id]['partner_id'] = partner_id
            users[user_id]['room'] = room_id

            users[partner_id]['partner_id'] = user_id
            users[partner_id]['room'] = room_id

            join_room(room_id)

            emit('partner_found', {
                'room': room_id,
                'partner_gender': users[partner_id]['gender'],
                'partner_name': users[partner_id].get('username', 'Stranger')
            }, room=room_id)
        else:
            add_to_queue(user_id, gender, partner_pref)
            emit('waiting', {'message': 'Looking for a stranger to chat with...'})

@socketio.on('stop_chat')
def handle_stop_chat():
    user_id = session.get('user_id')
    if not user_id or user_id not in users:
        return

    user = users[user_id]

    if user.get('room'):
        leave_room(user['room'])
        emit('chat_ended', {'message': 'Chat ended'}, room=user['room'])

        if user.get('partner_id') and user['partner_id'] in users:
            partner = users[user['partner_id']]
            emit('partner_left', room=partner.get('room'))

    user['partner_id'] = None
    user['room'] = None
    user['messages_sent'] = 0
    remove_from_queue(user_id)

    emit('chat_stopped', {'message': 'You have left the chat'})

@socketio.on('report_partner')
def handle_report(data):
    user_id = session.get('user_id')
    if not user_id or user_id not in users:
        return

    reason = data.get('reason', 'No reason provided')
    print(f'Report: User {user_id} reported partner {users[user_id].get("partner_id")} for: {reason}')

    handle_next_partner_internal(user_id)

# ============ FRIEND SYSTEM ============

@socketio.on('add_friend')
def handle_add_friend(data):
    """Send a friend request to another user"""
    user_id = session.get('user_id')
    if not user_id or user_id not in users:
        emit('friend_error', {'message': 'Please login first'})
        return

    target_username = data.get('username', '').strip()
    if not target_username:
        emit('friend_error', {'message': 'Username required'})
        return

    # Find target user
    target_user_id = None
    for uid, user_data in users.items():
        if user_data.get('username', '').lower() == target_username.lower():
            target_user_id = uid
            break

    # Also check registered users
    if not target_user_id:
        for uid, user_data in registered_users.items():
            if user_data.get('username', '').lower() == target_username.lower():
                target_user_id = uid
                break

    if not target_user_id:
        emit('friend_error', {'message': 'User not found'})
        return

    if target_user_id == user_id:
        emit('friend_error', {'message': 'Cannot add yourself'})
        return

    # Check if already friends
    if user_id in friends and target_user_id in friends[user_id]:
        emit('friend_error', {'message': 'Already friends'})
        return

    # Send friend request
    if target_user_id not in friend_requests:
        friend_requests[target_user_id] = []
    friend_requests[target_user_id].append(user_id)

    # Notify the request sender
    emit('friend_request_sent', {'message': f'Friend request sent to {target_username}'})

    # Notify the target user if online
    if target_user_id in users:
        emit('new_friend_request', {
            'from_user': users[user_id].get('username', 'Unknown'),
            'from_gender': users[user_id].get('gender', 'unknown')
        }, room=target_user_id)

@socketio.on('accept_friend')
def handle_accept_friend(data):
    """Accept a friend request"""
    user_id = session.get('user_id')
    if not user_id or user_id not in users:
        emit('friend_error', {'message': 'Please login first'})
        return

    from_user_id = data.get('user_id')
    if not from_user_id:
        emit('friend_error', {'message': 'User ID required'})
        return

    # Check if request exists
    if user_id not in friend_requests or from_user_id not in friend_requests[user_id]:
        emit('friend_error', {'message': 'No friend request from this user'})
        return

    # Remove from requests
    friend_requests[user_id].remove(from_user_id)

    # Add to friends
    if user_id not in friends:
        friends[user_id] = []
    if from_user_id not in friends[user_id]:
        friends[user_id].append(from_user_id)

    if from_user_id not in friends:
        friends[from_user_id] = []
    if user_id not in friends[from_user_id]:
        friends[from_user_id].append(user_id)

    from_username = users.get(from_user_id, {}).get('username', 'Unknown')
    emit('friend_accepted', {'message': f'You are now friends with {from_username}'})

@socketio.on('get_friends')
def handle_get_friends():
    """Get user's friends list"""
    user_id = session.get('user_id')
    if not user_id or user_id not in users:
        emit('friend_error', {'message': 'Please login first'})
        return

    user_friends = friends.get(user_id, [])
    friends_list = []

    for friend_id in user_friends:
        friend_info = {'id': friend_id}
        if friend_id in users:
            friend_info['username'] = users[friend_id].get('username', 'Unknown')
            friend_info['gender'] = users[friend_id].get('gender', 'unknown')
            friend_info['online'] = True
        elif friend_id in registered_users:
            friend_info['username'] = registered_users[friend_id].get('username', 'Unknown')
            friend_info['gender'] = registered_users[friend_id].get('gender', 'unknown')
            friend_info['online'] = False
        friends_list.append(friend_info)

    emit('friends_list', {'friends': friends_list})

def handle_next_partner_internal(user_id):
    if user_id not in users:
        return

    user = users[user_id]

    if user.get('room'):
        leave_room(user['room'])

    user['partner_id'] = None
    user['room'] = None
    user['messages_sent'] = 0

    gender = user.get('gender')
    partner_pref = user.get('partner_pref')

    if gender and partner_pref:
        partner_id = find_partner(user_id, gender, partner_pref)

        if partner_id and partner_id in users:
            room_id = create_chat_room(user_id, partner_id)

            users[user_id]['partner_id'] = partner_id
            users[user_id]['room'] = room_id

            users[partner_id]['partner_id'] = user_id
            users[partner_id]['room'] = room_id

            join_room(room_id)

            emit('partner_found', {
                'room': room_id,
                'partner_gender': users[partner_id]['gender'],
                'partner_name': users[partner_id].get('username', 'Stranger')
            }, room=room_id)
        else:
            add_to_queue(user_id, gender, partner_pref)
            emit('waiting', {'message': 'Looking for a stranger to chat with...'}, room=request.sid)

# ==================== PAGE ROUTES ====================

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/chat')
def main_chat():
    return render_template('main_chat.html')

@app.route('/chat-rooms')
def chat_rooms():
    return render_template('chat_rooms.html')

@app.route('/random-chat')
def random_chat():
    return render_template('random_chat.html')

@app.route('/dating-channels')
def dating_channels_page():
    return render_template('dating_channels.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/blog')
def blog_page():
    return render_template('blog.html')

@app.route('/faq')
def faq_page():
    return render_template('faq.html')

@app.route('/terms')
def terms_page():
    return render_template('terms.html')

@app.route('/privacy')
def privacy_page():
    return render_template('privacy.html')

@app.route('/safety')
def safety_page():
    return render_template('safety.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

@app.route('/welcome')
def welcome_page():
    return render_template('welcome.html')

@app.route('/ai-chat')
def ai_chat_page():
    return render_template('ai_chat.html')

@app.route('/chat/1on1')
def chat_1on1_page():
    return render_template('chat_1on1.html')

@app.route('/rooms')
def rooms_page():
    return render_template('chat_rooms.html')

@app.route('/history')
def history_page():
    return render_template('history.html')

@app.route('/inbox')
def inbox_page():
    return render_template('inbox.html')

@app.route('/friends')
def friends_page():
    return render_template('friends.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/blog/<article_id>')
@app.route('/blog/<slug>')
def blog_article_page(slug):
    """Display a single blog post"""
    post = get_blog_post(slug)
    if post:
        return render_template('blog_article.html', post=post, page_title=post['title'])
    return render_template('error.html', message='Blog post not found'), 404

# Admin Routes
@app.route('/admin')
def admin_dashboard():
    """Admin dashboard - requires authentication"""
    # Check authentication
    if not session.get(ADMIN_AUTH_KEY):
        return render_template('admin_login.html')
    
    posts = get_blog_posts()
    images = get_uploaded_images()
    stats = get_online_stats()
    
    return render_template('admin.html',
                         page='dashboard',
                         post_count=len(posts),
                         page_views=len(posts) * 100,
                         online_count=stats['total'],
                         media_count=len(images),
                         recent_posts=posts[:5])

# All other admin routes
ADMIN_ROUTES = [
    'admin_blog_list', 'admin_blog_new', 'admin_blog_edit', 'admin_blog_save', 
    'admin_blog_delete', 'admin_media', 'admin_upload', 'admin_dashboard',
    'admin_health', 'admin_health_issues', 'admin_health_analytics'
]

@app.route('/admin/blog')
def admin_blog_list():
    """List all blog posts"""
    posts = get_blog_posts()
    return render_template('admin.html',
                         page='blog_list',
                         posts=posts)

@app.route('/admin/blog/new')
def admin_blog_new():
    """Create new blog post"""
    return render_template('admin.html',
                         page='blog_edit',
                         post=None)

@app.route('/admin/blog/edit/<slug>')
def admin_blog_edit(slug):
    """Edit existing blog post"""
    post = get_blog_post(slug)
    if post:
        return render_template('admin.html',
                             page='blog_edit',
                             post=post)
    return redirect(url_for('admin_blog_list'))

@app.route('/admin/blog/save', methods=['POST'])
def admin_blog_save():
    """Save blog post"""
    csrf_token = request.form.get('csrf_token', '')
    if not validate_csrf_token(csrf_token):
        return render_template('admin.html', page='blog_edit', message='Invalid CSRF token', message_type='error')
    
    title = request.form.get('title', '').strip()
    slug = request.form.get('slug', '').strip()
    content = request.form.get('content', '').strip()
    category = request.form.get('category', 'Tips').strip()
    date = request.form.get('date', '').strip()
    excerpt = request.form.get('excerpt', '').strip()
    meta_title = request.form.get('meta_title', '').strip()
    meta_description = request.form.get('meta_description', '').strip()
    
    # Handle file upload
    featured_image = None
    if 'featured_image' in request.files:
        file = request.files['featured_image']
        featured_image = handle_file_upload(file)
    
    if not title or not content:
        return render_template('admin.html',
                             page='blog_edit',
                             message='Title and content are required',
                             message_type='error')
    
    try:
        save_blog_post(title, slug, content, category, date, excerpt, meta_title, meta_description, featured_image)
        post = get_blog_post(slug or slugify(title))
        return render_template('admin.html',
                             page='blog_edit',
                             post=post,
                             message='Blog post saved successfully!',
                             message_type='success')
    except Exception as e:
        return render_template('admin.html',
                             page='blog_edit',
                             message=f'Error saving: {str(e)}',
                             message_type='error')

@app.route('/admin/blog/delete/<slug>', methods=['POST'])
def admin_blog_delete(slug):
    """Delete blog post"""
    csrf_token = request.form.get('csrf_token', '')
    if not validate_csrf_token(csrf_token):
        return render_template('admin.html', page='blog_list', message='Invalid CSRF token', message_type='error')
    
    if delete_blog_post(slug):
        return render_template('admin.html',
                             page='blog_list',
                             posts=get_blog_posts(),
                             message='Blog post deleted successfully!',
                             message_type='success')
    return render_template('admin.html',
                         page='blog_list',
                         posts=get_blog_posts(),
                         message='Post not found',
                         message_type='error')

@app.route('/admin/media')
def admin_media():
    """Media library"""
    images = get_uploaded_images()
    return render_template('admin.html',
                         page='media',
                         images=images)

@app.route('/admin/upload', methods=['GET', 'POST'])
def admin_upload():
    """Upload image"""
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token', '')
        if not validate_csrf_token(csrf_token):
            return render_template('admin.html', page='upload', message='Invalid CSRF token', message_type='error')
        
        if 'file' not in request.files:
            return render_template('admin.html', page='upload', message='No file selected', message_type='error')
        
        file = request.files['file']
        url = handle_file_upload(file)
        
        if url:
            return render_template('admin.html',
                                 page='upload',
                                 message=f'Image uploaded: {url}',
                                 message_type='success',
                                 uploaded_url=url)
        return render_template('admin.html',
                             page='upload',
                             message='Invalid file type. Allowed: png, jpg, jpeg, gif, webp',
                             message_type='error')
    
    return render_template('admin.html', page='upload')

# ==================== ADMIN AUTHENTICATION ====================

ADMIN_AUTH_KEY = 'admin_authenticated'

def require_admin(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get(ADMIN_AUTH_KEY):
            # Check for admin credentials in headers
            auth_header = request.headers.get('X-Admin-Auth', '')
            expected = f"{config.ADMIN_USERNAME}:{config.ADMIN_PASSWORD}"
            
            if auth_header == expected:
                session[ADMIN_AUTH_KEY] = True
                logger.info(f"Admin authenticated from {get_client_ip()}")
            else:
                logger.warning(f"Unauthorized admin access attempt from {get_client_ip()}")
                return jsonify({'error': 'Unauthorized'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

# Login endpoint for admin panel
@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    """Admin login endpoint"""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    client_ip = get_client_ip()
    
    # Rate limit
    if not check_rate_limit(client_ip, 'admin_login'):
        logger.warning(f"Admin login rate limit exceeded from {client_ip}")
        return jsonify({'success': False, 'message': 'Too many attempts'}), 429
    
    if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
        session[ADMIN_AUTH_KEY] = True
        session['admin_username'] = username
        logger.info(f"Admin logged in: {username} from {client_ip}")
        return jsonify({'success': True, 'message': 'Login successful'})
    
    logger.warning(f"Failed admin login attempt: {username} from {client_ip}")
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/admin/logout', methods=['POST'])
def api_admin_logout():
    """Admin logout endpoint"""
    session.pop(ADMIN_AUTH_KEY, None)
    session.pop('admin_username', None)
    return jsonify({'success': True})

@app.route('/api/admin/check', methods=['GET'])
def api_admin_check():
    """Check if admin is authenticated"""
    return jsonify({'authenticated': session.get(ADMIN_AUTH_KEY, False)})

# API routes for auth
@app.route('/api/login', methods=['POST'])
def api_login():
    client_ip = get_client_ip()
    
    # Rate limit login attempts
    if not check_rate_limit(client_ip, 'login'):
        logger.warning(f"Login rate limit exceeded from {client_ip}")
        return jsonify({'success': False, 'message': 'Too many attempts. Please wait.'}), 429
    
    data = request.get_json()
    email = data.get('email', '').lower()
    password = data.get('password', '')

    # Find user by email
    for uid, user_data in registered_users.items():
        if user_data.get('email', '').lower() == email:
            # In production, verify password hash
            session['user_id'] = uid
            session['username'] = user_data['username']
            session['login_time'] = time.time()
            logger.info(f"User logged in: {user_data['username']} from {client_ip}")
            return jsonify({'success': True})

    logger.warning(f"Failed login attempt for {email} from {client_ip}")
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    client_ip = get_client_ip()
    
    # Rate limit registration
    if not check_rate_limit(client_ip, 'register'):
        logger.warning(f"Registration rate limit exceeded from {client_ip}")
        return jsonify({'success': False, 'message': 'Too many registration attempts'}), 429
    
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    gender = data.get('gender', 'none')

    # Validate
    if not username or len(username) < 3 or len(username) > 20:
        return jsonify({'success': False, 'message': 'Username must be 3-20 characters'})

    if not email:
        return jsonify({'success': False, 'message': 'Email required'})

    if not password or len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'})

    # Check if email exists
    for user_data in registered_users.values():
        if user_data.get('email', '').lower() == email:
            return jsonify({'success': False, 'message': 'Email already registered'})

    user_id = generate_user_id()
    registered_users[user_id] = {
        'username': username,
        'email': email,
        'gender': gender,
        'created_at': time.time()
    }

    session['user_id'] = user_id
    session['username'] = username

    return jsonify({'success': True})

# ==================== ADMIN ROUTES ====================

@app.route('/offline')
def offline_page():
    """Offline page for PWA"""
    return render_template('offline.html')

@app.route('/admin')
def admin_page():
    """Admin dashboard"""
    return render_template('admin.html')

# ==================== MESSAGE SEARCH API ====================

@app.route('/api/messages/search')
def search_messages():
    """Search messages"""
    query = request.args.get('q', '')
    user_id = session.get('user_id')

    if not user_id or not query:
        return jsonify({'success': False, 'messages': []})

    # Search in messages
    messages = database.search_messages(user_id, query)
    return jsonify({'success': True, 'messages': messages})

@app.route('/api/admin/stats')
def admin_stats():
    """Get admin dashboard stats"""
    stats = admin.get_dashboard_stats()
    return jsonify({'success': True, 'data': stats})

@app.route('/api/admin/users')
def admin_users():
    """Get all users"""
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    users = admin.get_all_users(limit, offset)
    return jsonify({'success': True, 'data': users})

@app.route('/api/admin/users/<user_id>')
def admin_user_detail(user_id):
    """Get user detail"""
    user = admin.get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    return jsonify({'success': True, 'data': user})

@app.route('/api/online/all')
def get_all_online_users():
    """Get all online users including guests"""
    from flask import jsonify
    users_list = []
    
    # Get users from active_connections (includes both registered and guest users)
    for sid, conn in active_connections.items():
        username = conn.get('username') or 'Guest'
        gender = conn.get('gender', 'unknown')
        country = conn.get('country', '')
        users_list.append({
            'id': sid,
            'username': username,
            'gender': gender,
            'country': country,
            'is_guest': conn.get('is_guest', False)
        })
    
    return jsonify({
        'success': True,
        'data': {
            'users': users_list,
            'count': len(users_list)
        }
    })

@app.route('/api/admin/users/search')
def admin_search_users():
    """Search users"""
    query = request.args.get('q', '')
    users = admin.search_users(query)
    return jsonify({'success': True, 'data': users})

@app.route('/api/admin/users/<user_id>/ban', methods=['POST'])
def admin_ban_user(user_id):
    """Ban a user"""
    admin.update_user_status(user_id, is_banned=True)
    return jsonify({'success': True, 'message': 'User banned'})

@app.route('/api/admin/users/<user_id>/unban', methods=['POST'])
def admin_unban_user(user_id):
    """Unban a user"""
    admin.update_user_status(user_id, is_banned=False)
    return jsonify({'success': True, 'message': 'User unbanned'})

@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    """Delete a user"""
    admin.delete_user(user_id)
    return jsonify({'success': True, 'message': 'User deleted'})

@app.route('/api/admin/messages')
def admin_messages():
    """Get recent messages"""
    limit = int(request.args.get('limit', 100))
    messages = admin.get_recent_messages(limit)
    return jsonify({'success': True, 'data': messages})

@app.route('/api/admin/messages/<int:message_id>', methods=['DELETE'])
def admin_delete_message(message_id):
    """Delete a message"""
    admin.delete_message(message_id)
    return jsonify({'success': True, 'message': 'Message deleted'})

@app.route('/api/admin/messages/search')
def admin_search_messages():
    """Search messages"""
    query = request.args.get('q', '')
    messages = admin.search_messages(query)
    return jsonify({'success': True, 'data': messages})

@app.route('/api/admin/reports')
def admin_reports():
    """Get reports"""
    status = request.args.get('status', 'pending')
    reports = admin.get_all_reports(status)
    return jsonify({'success': True, 'data': reports})

@app.route('/api/admin/reports/<int:report_id>', methods=['PUT'])
def admin_update_report(report_id):
    """Update report status"""
    data = request.get_json()
    status = data.get('status', 'reviewed')
    admin.update_report_status(report_id, status)
    return jsonify({'success': True, 'message': 'Report updated'})

@app.route('/api/admin/activity')
def admin_activity():
    """Get activity stats"""
    days = int(request.args.get('days', 7))
    stats = admin.get_activity_stats(days)
    return jsonify({'success': True, 'data': stats})

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Custom 404 error page"""
    return render_template('error.html', error_code=404, error_message='Page Not Found', error_description='The page you are looking for does not exist.'), 404

@app.errorhandler(500)
def internal_error(error):
    """Custom 500 error page"""
    return render_template('error.html', error_code=500, error_message='Internal Server Error', error_description='Something went wrong on our end. Please try again later.'), 500

@app.errorhandler(403)
def forbidden(error):
    """Custom 403 error page"""
    return render_template('error.html', error_code=403, error_message='Forbidden', error_description='You do not have permission to access this resource.'), 403

@app.errorhandler(400)
def bad_request(error):
    """Custom 400 error page"""
    return render_template('error.html', error_code=400, error_message='Bad Request', error_description='The request could not be understood by the server.'), 400

# ==================== REAL-TIME USER COUNT API ENDPOINTS ====================

@app.route('/api/online/count')
def get_online_count():
    """Get real-time online user count"""
    return jsonify({
        'success': True,
        'data': {
            'total_online': len(active_connections),
            'timestamp': time.time()
        }
    })

@app.route('/api/online/users')
def get_online_users_list():
    """Get list of online users (limited info for privacy)"""
    users_list = []
    for sid, conn in active_connections.items():
        if conn.get('username'):
            users_list.append({
                'id': conn.get('user_id'),
                'username': conn.get('username', 'Anonymous'),
                'gender': conn.get('gender', 'unknown'),
                'country': conn.get('country', ''),
                'room': conn.get('current_room', 'lobby')
            })
    
    return jsonify({
        'success': True,
        'data': {
            'users': users_list[:50],  # Limit to 50 for performance
            'count': len(users_list)
        }
    })

@app.route('/api/rooms/stats')
def get_room_stats():
    """Get chat room statistics with real user counts"""
    room_stats = {}
    
    # Count users per room
    for sid, conn in active_connections.items():
        room_id = conn.get('current_room', 'lobby')
        if room_id not in room_stats:
            room_stats[room_id] = {'users': 0, 'gender_counts': {'male': 0, 'female': 0, 'other': 0}}
        room_stats[room_id]['users'] += 1
        gender = conn.get('gender', 'other')
        if gender in room_stats[room_id]['gender_counts']:
            room_stats[room_id]['gender_counts'][gender] += 1
    
    return jsonify({
        'success': True,
        'data': room_stats
    })

# Admin Panel Routes
def load_content_data():
    """Load content data from JSON file"""
    data_file = 'data/content.json'
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'faqs': [], 'blogs': []}
    return {'faqs': [], 'blogs': []}

def get_online_stats():
    """Get online user statistics"""
    total = len(active_connections)
    guests = sum(1 for c in active_connections.values() if c.get('is_guest'))
    registered = total - guests
    return {'total': total, 'guests': guests, 'registered': registered}

@app.route('/api/debug/connections')
def debug_connections():
    """Debug endpoint to check active connections"""
    return jsonify({
        'success': True,
        'data': {
            'total_connections': len(active_connections),
            'session_info': {
                'user_id': session.get('user_id'),
                'username': session.get('username') or session.get('guest_username'),
                'gender': session.get('gender') or session.get('guest_gender'),
                'is_guest': session.get('is_guest'),
                'session_id': session.get('sid')
            },
            'connections': [
                {
                    'sid': sid,
                    'username': conn.get('username'),
                    'gender': conn.get('gender'),
                    'is_guest': conn.get('is_guest'),
                    'connected_at': conn.get('connected_at')
                }
                for sid, conn in active_connections.items()
            ]
        }
    })

@app.route('/api/ping', methods=['POST'])
def ping():
    """Keep-alive endpoint - updates user's last seen timestamp"""
    current_time = time.time()
    
    # Try to find connection by session
    sid = None
    for conn_sid, conn in active_connections.items():
        if conn.get('session_id') == session.get('sid'):
            sid = conn_sid
            break
    
    # Fall back to request.sid if available
    if not sid and hasattr(request, 'sid'):
        sid = request.sid
    
    if sid and sid in active_connections:
        active_connections[sid]['last_ping'] = current_time
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Not connected'})

def save_content_data(data):
    """Save content data to JSON file"""
    data_file = 'data/content.json'
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def generate_faq_html(faqs):
    """Generate FAQ HTML from FAQ list"""
    html = '''{% extends "base.html" %}

{% block title %}FAQ - Chat Online{% endblock %}

{% block content %}
<div class="content-page-container">
    <div class="content-page-header">
        <h1><i class="fas fa-question-circle"></i> Frequently Asked Questions</h1>
        <p>Find answers to common questions</p>
    </div>
    <div class="accordion">
'''
    for faq in faqs:
        html += f'''        <div class="accordion-item">
            <button class="accordion-header">
                <span><i class="fas {faq['icon']}"></i> {faq['question']}</span>
                <i class="fas fa-chevron-down"></i>
            </button>
            <div class="accordion-content">
                <div class="accordion-body">
                    <p>{faq['answer']}</p>
                </div>
            </div>
        </div>
'''
    html += '''    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', function() {
        const item = this.parentElement;
        const isActive = item.classList.contains('active');

        document.querySelectorAll('.accordion-item').forEach(otherItem => {
            otherItem.classList.remove('active');
        });

        if (!isActive) {
            item.classList.add('active');
        }
    });
});
</script>
{% endblock %}'''
    return html

def generate_blog_html(blogs):
    """Generate Blog HTML from blog list"""
    html = '''{% extends "base.html" %}

{% block title %}Blog - Chat Online{% endblock %}

{% block content %}
<div class="content-page-container">
    <div class="content-page-header">
        <h1><i class="fas fa-blog"></i> Blog</h1>
        <p>Latest tips, news, and articles</p>
    </div>
    <div class="blog-grid">
'''
    for blog in blogs:
        bg_colors = [
            'linear-gradient(135deg, #0EA5E9, #06B6D4)',
            'linear-gradient(135deg, #8B5CF6, #7C3AED)',
            'linear-gradient(135deg, #10B981, #059669)',
            'linear-gradient(135deg, #F59E0B, #D97706)',
            'linear-gradient(135deg, #EC4899, #DB2777)',
            'linear-gradient(135deg, #6366F1, #4F46E5)'
        ]
        color = bg_colors[hash(blog['title']) % len(bg_colors)]
        icon = 'fa-star' if blog['category'] == 'Safety' else 'fa-user-friends' if blog['category'] == 'Community' else 'fa-lightbulb' if blog['category'] == 'Tips' else 'fa-globe'
        html += f'''
        <div class="blog-card">
            <div class="blog-image" style="background: {color};">
                <i class="fas {icon}"></i>
            </div>
            <div class="blog-content">
                <span class="blog-category">{blog['category']}</span>
                <h3>{blog['title']}</h3>
                <p>{blog['content'][:100]}...</p>
                <span class="blog-meta"><i class="fas fa-calendar"></i> {blog['date']}</span>
            </div>
        </div>
'''
    html += '''    </div>
</div>
{% endblock %}'''
    return html

@app.route('/admin')
def admin_panel():
    """Admin dashboard"""
    data = load_content_data()
    # Count online users by type
    total = len(active_connections)
    guests = sum(1 for c in active_connections.values() if c.get('is_guest'))
    registered = total - guests
    return render_template('admin.html', 
                         page='dashboard',
                         page_title='Dashboard',
                         faq_count=len(data.get('faqs', [])),
                         blog_count=len(data.get('blogs', [])),
                         online_count=total,
                         online_guests=guests,
                         online_registered=registered)

@app.route('/admin/edit/<page>')
def edit_page(page):
    """Edit any content page"""
    page_files = {
        'faq': ('templates/faq.html', 'FAQ Page', 'faq'),
        'about': ('templates/about.html', 'About Page', 'about'),
        'blog': ('templates/blog.html', 'Blog Page', 'blog'),
        'contact': ('templates/contact.html', 'Contact Page', 'contact'),
        'privacy': ('templates/privacy.html', 'Privacy Policy', 'privacy'),
        'terms': ('templates/terms.html', 'Terms of Service', 'terms'),
        'safety': ('templates/safety.html', 'Safety Guidelines', 'safety')
    }
    
    if page not in page_files:
        return render_template('admin.html', page='dashboard', page_title='Dashboard', message='Page not found', message_type='error')
    
    file_path = page_files[page][0]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return render_template('admin.html', 
                         page='edit_page',
                         page_key=page,
                         page_title=page_files[page][1],
                         content=content)

@app.route('/admin/edit/<page>', methods=['POST'])
def save_page(page):
    """Save page content"""
    page_files = {
        'faq': ('templates/faq.html', 'FAQ Page'),
        'about': ('templates/about.html', 'About Page'),
        'blog': ('templates/blog.html', 'Blog Page'),
        'contact': ('templates/contact.html', 'Contact Page'),
        'privacy': ('templates/privacy.html', 'Privacy Policy'),
        'terms': ('templates/terms.html', 'Terms of Service'),
        'safety': ('templates/safety.html', 'Safety Guidelines')
    }
    
    if page not in page_files:
        return render_template('admin.html', page='dashboard', page_title='Dashboard', message='Page not found', message_type='error')
    
    file_path = page_files[page][0]
    new_content = request.form.get('content', '')
    
    csrf_token = request.form.get('csrf_token', '')
    if not validate_csrf_token(csrf_token):
        return render_template('admin.html', page='edit_page', page_key=page, page_title=page_files[page][1], content=new_content, message='Invalid CSRF token', message_type='error')
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return render_template('admin.html', page='edit_page', page_key=page, page_title=page_files[page][1], content=new_content, message='Changes saved successfully!', message_type='success')
    except Exception as e:
        return render_template('admin.html', page='edit_page', page_key=page, page_title=page_files[page][1], content=new_content, message=f'Error saving: {str(e)}', message_type='error')

@app.route('/admin/manage/faq')
def manage_faq():
    """Manage FAQ items"""
    data = load_content_data()
    faqs = data.get('faqs', [])
    return render_template('admin.html',
                         page='manage_faq',
                         faqs=faqs,
                         faqs_json=json.dumps(faqs))

@app.route('/admin/manage/blog')
def manage_blog():
    """Manage blog posts"""
    data = load_content_data()
    blogs = data.get('blogs', [])
    return render_template('admin.html',
                         page='manage_blog',
                         blogs=blogs,
                         blogs_json=json.dumps(blogs))

@app.route('/admin/save/faq', methods=['POST'])
def save_faq():
    """Add or edit FAQ item"""
    csrf_token = request.form.get('csrf_token', '')
    if not validate_csrf_token(csrf_token):
        return render_template('admin.html', page='manage_faq', faqs=load_content_data().get('faqs', []), message='Invalid CSRF token', message_type='error')
    
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    icon = request.form.get('icon', 'fa-question-circle')
    index = request.form.get('faq_index', '')
    
    if not question or not answer:
        data = load_content_data()
        return render_template('admin.html', page='manage_faq', faqs=data.get('faqs', []), faqs_json=json.dumps(data.get('faqs', [])), message='Question and answer are required', message_type='error')
    
    data = load_content_data()
    faq = {'question': question, 'answer': answer, 'icon': icon}
    
    if index:
        try:
            idx = int(index)
            if 0 <= idx < len(data['faqs']):
                data['faqs'][idx] = faq
            else:
                data['faqs'].append(faq)
        except:
            data['faqs'].append(faq)
    else:
        data['faqs'].append(faq)
    
    save_content_data(data)
    
    # Regenerate FAQ HTML
    with open('templates/faq.html', 'w', encoding='utf-8') as f:
        f.write(generate_faq_html(data['faqs']))
    
    return render_template('admin.html', page='manage_faq', faqs=data.get('faqs', []), faqs_json=json.dumps(data.get('faqs', [])), message='FAQ saved successfully!', message_type='success')

@app.route('/admin/delete/faq/<int:index>', methods=['POST'])
def delete_faq(index):
    """Delete FAQ item"""
    csrf_token = request.form.get('csrf_token', '')
    if not validate_csrf_token(csrf_token):
        return render_template('admin.html', page='manage_faq', faqs=load_content_data().get('faqs', []), message='Invalid CSRF token', message_type='error')
    
    data = load_content_data()
    
    try:
        if 0 <= index < len(data['faqs']):
            del data['faqs'][index]
            save_content_data(data)
            
            # Regenerate FAQ HTML
            with open('templates/faq.html', 'w', encoding='utf-8') as f:
                f.write(generate_faq_html(data['faqs']))
            
            message = 'FAQ deleted successfully!'
        else:
            message = 'FAQ not found!'
    except Exception as e:
        message = f'Error: {str(e)}'
    
    return render_template('admin.html', page='manage_faq', faqs=data.get('faqs', []), faqs_json=json.dumps(data.get('faqs', [])), message=message, message_type='success')

@app.route('/admin/save/blog', methods=['POST'])
def save_blog():
    """Add or edit blog post"""
    csrf_token = request.form.get('csrf_token', '')
    if not validate_csrf_token(csrf_token):
        return render_template('admin.html', page='manage_blog', blogs=load_content_data().get('blogs', []), message='Invalid CSRF token', message_type='error')
    
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'Tips')
    date = request.form.get('date', '')
    content = request.form.get('content', '').strip()
    index = request.form.get('blog_index', '')
    
    if not title or not date or not content:
        data = load_content_data()
        return render_template('admin.html', page='manage_blog', blogs=data.get('blogs', []), blogs_json=json.dumps(data.get('blogs', [])), message='Title, date, and content are required', message_type='error')
    
    data = load_content_data()
    blog = {'title': title, 'category': category, 'date': date, 'content': content}
    
    if index:
        try:
            idx = int(index)
            if 0 <= idx < len(data['blogs']):
                data['blogs'][idx] = blog
            else:
                data['blogs'].insert(0, blog)
        except:
            data['blogs'].insert(0, blog)
    else:
        data['blogs'].insert(0, blog)
    
    save_content_data(data)
    
    # Regenerate Blog HTML
    with open('templates/blog.html', 'w', encoding='utf-8') as f:
        f.write(generate_blog_html(data['blogs']))
    
    return render_template('admin.html', page='manage_blog', blogs=data.get('blogs', []), blogs_json=json.dumps(data.get('blogs', [])), message='Blog post saved successfully!', message_type='success')

@app.route('/admin/delete/blog/<int:index>', methods=['POST'])
def delete_blog(index):
    """Delete blog post"""
    csrf_token = request.form.get('csrf_token', '')
    if not validate_csrf_token(csrf_token):
        return render_template('admin.html', page='manage_blog', blogs=load_content_data().get('blogs', []), message='Invalid CSRF token', message_type='error')
    
    data = load_content_data()
    
    try:
        if 0 <= index < len(data['blogs']):
            del data['blogs'][index]
            save_content_data(data)
            
            # Regenerate Blog HTML
            with open('templates/blog.html', 'w', encoding='utf-8') as f:
                f.write(generate_blog_html(data['blogs']))
            
            message = 'Blog post deleted successfully!'
        else:
            message = 'Blog post not found!'
    except Exception as e:
        message = f'Error: {str(e)}'
    
    return render_template('admin.html', page='manage_blog', blogs=data.get('blogs', []), blogs_json=json.dumps(data.get('blogs', [])), message=message, message_type='success')

# ==================== HEALTH MONITORING ====================

# Health monitoring storage
health_data = {
    'page_load_times': [],
    'errors': [],
    'page_views': [],
    '404_pages': [],
    'login_failures': [],
    'suspicious_activity': [],
    'startup_time': datetime.now(),
    'checks': {}
}

def log_error(error_type, message, path='', details=None):
    """Log an error for tracking"""
    error = {
        'type': error_type,
        'message': message,
        'path': path,
        'details': details,
        'timestamp': datetime.now().isoformat(),
        'ip': get_client_ip()
    }
    health_data['errors'].append(error)
    # Keep only last 100 errors
    if len(health_data['errors']) > 100:
        health_data['errors'] = health_data['errors'][-100:]
    return error

def log_page_view(page, user_type='guest'):
    """Log a page view"""
    view = {
        'page': page,
        'user_type': user_type,
        'timestamp': datetime.now().isoformat(),
        'ip': get_client_ip()
    }
    health_data['page_views'].append(view)
    # Keep only last 1000 views
    if len(health_data['page_views']) > 1000:
        health_data['page_views'] = health_data['page_views'][-1000:]

def log_404(page):
    """Log a 404 page"""
    error = {
        'page': page,
        'timestamp': datetime.now().isoformat(),
        'ip': get_client_ip()
    }
    health_data['404_pages'].append(error)
    if len(health_data['404_pages']) > 50:
        health_data['404_pages'] = health_data['404_pages'][-50:]

def get_health_status():
    """Get current health status"""
    checks = {
        'overall': 'healthy',
        'database': {'status': 'unknown'},
        'memory': {'status': 'unknown'},
        'disk': {'status': 'unknown'},
        'socket': {'status': 'unknown'},
        'uptime': {'status': 'unknown'}
    }
    
    # Check database
    try:
        start = time.time()
        db = get_db()
        db.execute('SELECT 1')
        elapsed = (time.time() - start) * 1000
        checks['database'] = {'status': 'healthy', 'response_time_ms': round(elapsed, 2)}
    except Exception as e:
        checks['database'] = {'status': 'error', 'message': str(e)}
        checks['overall'] = 'critical'
    
    # Check memory
    try:
        import psutil
        mem = psutil.virtual_memory()
        checks['memory'] = {
            'status': 'warning' if mem.percent > 80 else 'healthy',
            'percent_used': mem.percent,
            'total_gb': round(mem.total / (1024**3), 2)
        }
        if mem.percent > 90:
            checks['overall'] = 'critical'
        elif mem.percent > 80:
            checks['overall'] = 'warning'
    except:
        pass
    
    # Check disk
    try:
        import psutil
        usage = psutil.disk_usage('/')
        checks['disk'] = {
            'status': 'warning' if usage.percent > 80 else 'healthy',
            'percent_used': usage.percent
        }
    except:
        pass
    
    # Check socket connections
    total = len(active_connections)
    guests = sum(1 for c in active_connections.values() if c.get('is_guest'))
    checks['socket'] = {
        'status': 'healthy',
        'total_connections': total,
        'guests': guests,
        'registered': total - guests
    }
    
    # Check uptime
    uptime = datetime.now() - health_data['startup_time']
    checks['uptime'] = {
        'status': 'healthy',
        'hours': round(uptime.total_seconds() / 3600, 2)
    }
    
    return checks

def get_analytics(days=1):
    """Get analytics data"""
    cutoff = datetime.now() - timedelta(days=days)
    views = [v for v in health_data['page_views'] if datetime.fromisoformat(v['timestamp']) > cutoff]
    
    page_counts = {}
    for view in views:
        page = view['page']
        page_counts[page] = page_counts.get(page, 0) + 1
    
    popular_pages = sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    
    return {
        'period_days': days,
        'total_views': len(views),
        'unique_pages': len(page_counts),
        'popular_pages': [{'page': p[0], 'views': p[1]} for p in popular_pages],
        'errors_count': len([e for e in health_data['errors'] if datetime.fromisoformat(e['timestamp']) > cutoff]),
        '404_count': len([e for e in health_data['404_pages'] if datetime.fromisoformat(e['timestamp']) > cutoff])
    }

def get_all_issues():
    """Get all current issues"""
    issues = []
    checks = get_health_status()
    
    # Check for warnings in health
    for check_name, check_data in checks.items():
        if check_name == 'overall':
            continue
        if check_data.get('status') == 'warning':
            issues.append({
                'type': 'warning',
                'source': check_name,
                'message': f"{check_name} has warnings"
            })
    
    # Add recent errors
    recent_errors = health_data['errors'][-10:]
    for error in recent_errors:
        issues.append({
            'type': 'error',
            'source': error['type'],
            'message': error['message'],
            'path': error.get('path', '')
        })
    
    # Add recent 404s
    for error in health_data['404_pages'][-5:]:
        issues.append({
            'type': '404',
            'source': 'broken_link',
            'message': f"404: {error['page']}",
            'path': error['page']
        })
    
    return issues

# Health monitoring routes
@app.route('/admin/health')
def admin_health():
    """Health dashboard"""
    checks = get_health_status()
    analytics = get_analytics(1)
    issues = get_all_issues()
    
    return render_template('health_dashboard.html',
                         page='health',
                         overall_status=checks['overall'],
                         checks=checks,
                         analytics=analytics,
                         issues=issues,
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/admin/health/issues')
def admin_health_issues():
    """All issues"""
    issues = get_all_issues()
    return render_template('health_dashboard.html',
                         page='issues',
                         issues=issues,
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/admin/health/analytics')
def admin_health_analytics():
    """Analytics"""
    analytics = get_analytics(7)
    return render_template('health_dashboard.html',
                         page='analytics',
                         analytics=analytics,
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/api/health')
def api_health():
    """Health check API"""
    checks = get_health_status()
    issues = get_all_issues()
    return jsonify({
        'success': True,
        'data': {
            'checks': checks,
            'issues_count': len(issues)
        }
    })

@app.route('/api/health/errors')
def api_health_errors():
    """Get recent errors"""
    return jsonify({
        'success': True,
        'data': health_data['errors'][-20:]
    })

@app.route('/api/health/analytics')
def api_analytics():
    """Analytics API"""
    return jsonify({
        'success': True,
        'data': get_analytics(7)
    })

@app.route('/api/log-error', methods=['POST'])
def api_log_error():
    """Log an error from client"""
    data = request.get_json()
    log_error(
        error_type=data.get('type', 'unknown'),
        message=data.get('message', ''),
        path=data.get('path', ''),
        details=data.get('details', {})
    )
    return jsonify({'success': True})

@app.route('/api/log-pageview', methods=['POST'])
def api_log_pageview():
    """Log a page view"""
    data = request.get_json()
    log_page_view(
        page=data.get('page', ''),
        user_type=data.get('user_type', 'guest')
    )
    return jsonify({'success': True})

@app.route('/api/online/all')
def api_online_all():
    """Get all online users including current user - for welcome page user list"""
    online_users = []
    seen_ids = set()

    # Get all users from session (both guests and logged-in users)
    current_user_id = session.get('user_id')
    current_username = session.get('guest_username') or session.get('username')
    current_gender = session.get('guest_gender') or session.get('gender')
    current_country = session.get('guest_country') or session.get('country')
    is_guest = session.get('is_guest', False)

    # Add current user from session if logged in
    if current_user_id and current_username:
        current_user = {
            'id': current_user_id,
            'username': current_username,
            'gender': current_gender or '',
            'country': current_country or '',
            'is_guest': is_guest,
            'is_online': True,
            'last_seen': datetime.now().isoformat()
        }
        online_users.append(current_user)
        seen_ids.add(current_user_id)

    # Get all active socket connections (guest users + registered users connected via socket)
    for sid, conn in active_connections.items():
        user_id = conn.get('user_id')
        if user_id and user_id not in seen_ids:
            user_data = {
                'id': user_id,
                'username': conn.get('username', 'Guest'),
                'gender': conn.get('gender', ''),
                'country': conn.get('country', ''),
                'is_guest': conn.get('is_guest', False),
                'is_online': True,
                'last_seen': datetime.fromtimestamp(conn.get('connected_at', time.time())).isoformat()
            }
            online_users.append(user_data)
            seen_ids.add(user_id)

    # Get registered users from database who are online (not in seen_ids)
    try:
        from database import fetch_all, USE_POSTGRES
        if USE_POSTGRES:
            # PostgreSQL needs different approach for NOT IN with tuple
            if seen_ids:
                registered_online = fetch_all('''
                    SELECT id, username, gender, age, country, state, is_online, last_seen
                    FROM users
                    WHERE is_online = 1 AND id NOT IN %s
                    ORDER BY last_seen DESC
                    LIMIT 50
                ''', (tuple(seen_ids),))
            else:
                registered_online = fetch_all('''
                    SELECT id, username, gender, age, country, state, is_online, last_seen
                    FROM users
                    WHERE is_online = 1
                    ORDER BY last_seen DESC
                    LIMIT 50
                ''')

        for user in registered_online:
            user_dict = {
                'id': user.get('id'),
                'username': user.get('username'),
                'gender': user.get('gender', ''),
                'country': user.get('country', ''),
                'is_guest': False,
                'is_online': True,
                'last_seen': user.get('last_seen')
            }
            if user_dict['id'] not in seen_ids:
                online_users.append(user_dict)
    except Exception as e:
        pass  # Silently fail if DB query errors

    return jsonify({
        'success': True,
        'data': {
            'users': online_users,
            'count': len(online_users)
        }
    })

@app.route('/admin/health/pages')
def admin_health_pages():
    """Page views"""
    return jsonify({
        'success': True,
        'data': health_data['page_views'][-100:]
    })

if __name__ == '__main__':
    # For production, use eventlet
    try:
        import eventlet
        eventlet.monkey_patch()
        socketio.run(app, debug=False, port=int(os.environ.get('PORT', 5001)), host='0.0.0.0')
    except ImportError:
        socketio.run(app, debug=False, port=int(os.environ.get('PORT', 5001)), host='0.0.0.0')
