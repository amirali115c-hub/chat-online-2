"""
Admin blueprint — admin dashboard, blog management, media library routes.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
import os
import json
import time
from datetime import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Require admin authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return render_template('admin_login.html')
        return f(*args, **kwargs)
    return decorated


def get_uploaded_images():
    from app import UPLOAD_DIR, allowed_file
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


def get_online_stats():
    from app import active_connections
    total = len(active_connections)
    guests = sum(1 for c in active_connections.values() if c.get('is_guest'))
    return {'total': total, 'guests': guests, 'registered': total - guests}


# ── Dashboard ────────────────────────────────────────────────

@admin_bp.route('/')
@admin_required
def dashboard():
    from app import get_blog_posts
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


@admin_bp.route('/blog')
@admin_required
def blog_list():
    from app import get_blog_posts
    posts = get_blog_posts()
    return render_template('admin.html', page='blog_list', posts=posts)


@admin_bp.route('/blog/new')
@admin_required
def blog_new():
    return render_template('admin.html', page='blog_edit', post=None)


@admin_bp.route('/blog/edit/<slug>')
@admin_required
def blog_edit(slug):
    from app import get_blog_post
    post = get_blog_post(slug)
    if post:
        return render_template('admin.html', page='blog_edit', post=post)
    return redirect(url_for('admin.blog_list'))


@admin_bp.route('/blog/save', methods=['POST'])
@admin_required
def blog_save():
    from app import save_blog_post, handle_file_upload
    from app import csrf, validate_csrf_token

    csrf_token = request.form.get('csrf_token', '')
    if not validate_csrf_token(csrf_token):
        return render_template('admin.html', page='blog_edit',
                             message='Invalid CSRF token', message_type='error')

    title = request.form.get('title', '').strip()
    slug = request.form.get('slug', '').strip()
    content = request.form.get('content', '').strip()
    category = request.form.get('category', 'Tips').strip()
    date = request.form.get('date', '').strip()
    excerpt = request.form.get('excerpt', '').strip()
    meta_title = request.form.get('meta_title', '').strip()
    meta_description = request.form.get('meta_description', '').strip()

    featured_image = None
    if 'featured_image' in request.files:
        file = request.files['featured_image']
        featured_image = handle_file_upload(file)

    if not title or not content:
        return render_template('admin.html', page='blog_edit',
                             message='Title and content are required', message_type='error')

    try:
        saved_slug = save_blog_post(title, slug, content, category, date, excerpt,
                                   meta_title, meta_description, featured_image)
        from app import get_blog_post as _get
        post = _get(saved_slug or slug)
        return render_template('admin.html', page='blog_edit', post=post,
                             message='Blog post saved!', message_type='success')
    except Exception as e:
        return render_template('admin.html', page='blog_edit',
                             message=f'Error: {str(e)}', message_type='error')


@admin_bp.route('/blog/delete/<slug>', methods=['POST'])
@admin_required
def blog_delete(slug):
    from app import delete_blog_post, get_blog_posts
    from app import csrf, validate_csrf_token

    csrf_token = request.form.get('csrf_token', '')
    if not validate_csrf_token(csrf_token):
        return render_template('admin.html', page='blog_list',
                             posts=get_blog_posts(),
                             message='Invalid CSRF token', message_type='error')

    if delete_blog_post(slug):
        return render_template('admin.html', page='blog_list',
                             posts=get_blog_posts(),
                             message='Post deleted.', message_type='success')
    return render_template('admin.html', page='blog_list',
                         posts=get_blog_posts(),
                         message='Post not found.', message_type='error')


@admin_bp.route('/media')
@admin_required
def media():
    images = get_uploaded_images()
    return render_template('admin.html', page='media', images=images)


@admin_bp.route('/upload', methods=['GET', 'POST'])
@admin_required
def upload():
    if request.method == 'POST':
        from app import handle_file_upload, csrf, validate_csrf_token

        csrf_token = request.form.get('csrf_token', '')
        if not validate_csrf_token(csrf_token):
            return render_template('admin.html', page='upload',
                                 message='Invalid CSRF token', message_type='error')

        if 'file' not in request.files:
            return render_template('admin.html', page='upload',
                                 message='No file selected', message_type='error')

        file = request.files['file']
        url = handle_file_upload(file)

        if url:
            return render_template('admin.html', page='upload',
                                 message=f'Uploaded: {url}', message_type='success',
                                 uploaded_url=url)
        return render_template('admin.html', page='upload',
                             message='Invalid file type.', message_type='error')

    return render_template('admin.html', page='upload')


# ── Health monitoring ─────────────────────────────────────────

@admin_bp.route('/health')
@admin_required
def health():
    from app import get_health_status, get_analytics, get_all_issues
    checks = get_health_status()
    analytics = get_analytics(1)
    issues = get_all_issues()
    return render_template('admin.html',
                         page='health',
                         overall_status=checks['overall'],
                         checks=checks,
                         analytics=analytics,
                         issues=issues,
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


@admin_bp.route('/health/issues')
@admin_required
def health_issues():
    from app import get_all_issues
    issues = get_all_issues()
    return render_template('admin.html', page='issues', issues=issues,
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


@admin_bp.route('/health/analytics')
@admin_required
def health_analytics():
    from app import get_analytics
    analytics = get_analytics(7)
    return render_template('admin.html', page='analytics', analytics=analytics,
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
