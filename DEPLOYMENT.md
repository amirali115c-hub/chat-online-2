# Chat Online - Production Deployment Guide

## ✅ Production Ready Checklist

### Already Done:
- [x] Debug mode disabled
- [x] Secure session cookies
- [x] CSRF protection
- [x] Rate limiting
- [x] PWA manifest
- [x] Service worker
- [x] Mobile responsive

### To Deploy:

## Option 1: Simple VPS (DigitalOcean, Linode, AWS)

```bash
# 1. Upload files to server
scp -r . user@your-server:/var/www/chat-online

# 2. Install dependencies
cd /var/www/chat-online
pip install -r requirements.txt

# 3. Set environment variables
cp .env.example .env
nano .env  # Edit with real values

# 4. Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app --daemon

# 5. Setup nginx (recommended)
```

## Option 2: Render / Railway / Heroku

1. Push code to GitHub
2. Connect to Render/Railway
3. Set environment variables:
   - `SECRET_KEY` = generate random string
   - `DEBUG` = False
4. Deploy

## Option 3: Cloudflare (Recommended - Free SSL)

1. Point domain to your server IP
2. Enable Cloudflare
3. SSL/TLS: Full (Strict)
4. Automatically enables HTTPS

## Required Environment Variables:

```
SECRET_KEY=your-secure-random-key
DEBUG=False
```

## Testing Production Mode:

```bash
# Test locally with production settings
export DEBUG=False
python app.py
```

## For Live Website:

1. **Get a domain** (Namecheap, GoDaddy)
2. **Use Cloudflare** (free SSL)
3. **Deploy to VPS** (DigitalOcean $4/mo)
4. **Configure email** (optional)

## Quick Test:

Your server is already running in production mode at:
**http://192.168.0.102:5001**

For public access, you need to:
1. Deploy to a server with public IP
2. Set up domain and SSL
