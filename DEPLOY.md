# Chat Online - Production Deployment Guide

## Quick Start (Development Mode)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
# Server runs at http://localhost:5001
```

## Production Deployment

### Option 1: Using Gunicorn (Simple)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -k eventlet app:app --bind 0.0.0.0:5001
```

### Option 2: Using Nginx + Gunicorn (Recommended)

1. Install nginx
2. Configure nginx:

```nginx
# /etc/nginx/sites-available/chat-online

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /static {
        alias /path/to/chat_online/static;
        expires 30d;
    }
}
```

### Option 3: Using Cloudflare (Easiest)

1. Sign up at cloudflare.com
2. Add your domain
3. Use their free SSL
4. Point DNS to your server

## SSL/HTTPS Setup

### Using Let's Encrypt (Free)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Environment Variables

Create a `.env` file:

```
SECRET_KEY=your-secure-random-key
DEBUG=False
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password
```

## Production Checklist

- [x] Debug mode disabled
- [x] Secure session cookies
- [x] HTTPS enabled (via Cloudflare or Let's Encrypt)
- [x] Strong SECRET_KEY
- [x] Rate limiting enabled
- [x] Admin password changed

## Port Forwarding

If behind a router, forward port 80/443 to your server.

## Domain

Get a domain from:
- Namecheap
- GoDaddy
- Cloudflare (free)
