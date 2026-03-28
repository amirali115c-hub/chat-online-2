# 🚀 ChatOnline - Deployment Guide

## Quick Start (Development)
```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

## Production Deployment

### 1. Environment Variables (.env)
Update your `.env` file:

```env
# Required - Generate with: python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your_64_char_hex_key_here
JWT_SECRET=your_64_char_hex_key_here

# Production Settings
DEBUG=False
FLASK_ENV=production

# Admin
ADMIN_AUTH_KEY=your_secure_admin_key

# Database
DATABASE_URL=chatonline.db

# For HTTPS in production
SECURE_COOKIES=True
```

### 2. Install Production Dependencies
```bash
pip install eventlet gunicorn
```

### 3. Run with Gunicorn (Recommended)
```bash
gunicorn -w 4 -k eventlet app:app --bind 0.0.0.0:5000
```

### 4. Using the Provided Script
```bash
chmod +x run_production.sh
./run_production.sh
```

## Required Before Launch

### 1. Google Analytics
Edit `templates/base.html` and replace:
- `GA_MEASUREMENT_ID` → Your actual GA4 ID

### 2. Sentry Error Tracking (Optional)
Edit `templates/base.html` and replace:
- `YOUR_SENTRY_DSN_HERE` → Your Sentry DSN

### 3. Favicon
Replace `static/images/favicon.svg` with your actual logo

### 4. OG Image
Replace `static/images/og-image.jpg` (1200x630) for social sharing

## SSL/HTTPS Setup

Using Let's Encrypt with nginx:
```bash
sudo apt install nginx certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Performance Tips

1. Enable Gzip compression in nginx
2. Use CDN for static files (optional)
3. Set up database backups
4. Configure log rotation

## Troubleshooting

### Port Already in Use
```bash
lsof -i :5000
kill -9 <PID>
```

### Eventlet Import Error
```bash
pip install --upgrade eventlet
```
