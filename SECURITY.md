# Chat Online - Security & Configuration Guide

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Edit `.env` with your actual values:
```env
SECRET_KEY=your-super-secret-key-here
JWT_SECRET=your-jwt-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
```

### 3. Run the Application
```bash
python start.py
```

---

## Security Features Implemented

### 1. Environment-Based Configuration
All secrets are loaded from environment variables:
- `SECRET_KEY` - Flask session secret
- `JWT_SECRET` - JWT token signing key
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` - Admin panel credentials

### 2. Rate Limiting
- Login attempts: Limited per IP
- Registration: Limited per IP
- Messages: Limited per user
- Admin login: Limited per IP

### 3. Admin Authentication
Access admin panel at `/admin` requires:
- Username and password authentication
- Session-based auth token
- Rate limiting on login attempts

### 4. Comprehensive Logging
Logs are written to `logs/chat-online.log` with:
- Application startup/shutdown
- User connections/disconnections
- Login attempts (success/failure)
- Admin actions
- Error events
- Security events (blocked IPs, bot detection)

---

## Log File Location
```
logs/chat-online.log
```

### Log Levels
- `INFO` - Normal operations
- `WARNING` - Non-critical issues
- `ERROR` - Errors requiring attention
- `SECURITY` - Security events

---

## Production Checklist

Before deploying to production:

- [ ] Set `FLASK_ENV=production`
- [ ] Generate strong SECRET_KEY (32+ random characters)
- [ ] Generate strong JWT_SECRET (32+ random characters)
- [ ] Change default admin credentials
- [ ] Enable HTTPS
- [ ] Configure CORS for your domain
- [ ] Set up Redis for rate limiting storage
- [ ] Configure email for password reset
- [ ] Set up log rotation
- [ ] Configure backup strategy

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | Flask session secret key |
| `JWT_SECRET` | Yes | - | JWT signing secret |
| `DATABASE_URL` | No | SQLite | Database connection URL |
| `FLASK_ENV` | No | development | Environment (development/production) |
| `ADMIN_USERNAME` | No | admin | Admin panel username |
| `ADMIN_PASSWORD` | No | admin123 | Admin panel password |
| `LOG_LEVEL` | No | INFO | Logging level |
| `SESSION_COOKIE_SECURE` | No | false | Require HTTPS for cookies |
| `SESSION_COOKIE_HTTPONLY` | No | true | HttpOnly cookies |
| `SESSION_COOKIE_SAMESITE` | No | Lax | SameSite policy |

---

## Monitoring

### View Logs
```bash
# View live logs
tail -f logs/chat-online.log

# View errors only
grep "ERROR" logs/chat-online.log

# View security events
grep "SECURITY\|WARNING" logs/chat-online.log
```

### Health Check
```bash
curl http://localhost:5000/health
```

### Admin Health Dashboard
Visit: `/admin/health`

---

## Troubleshooting

### Admin panel returns 401 Unauthorized
1. Check credentials in `.env`
2. Verify session cookie
3. Clear browser cache

### Rate limited too often
1. Check logs for your IP
2. Wait for rate limit to reset (1 hour)
3. If legitimate, adjust `RATELIMIT_DEFAULT`

### Logs not writing
1. Check `logs/` directory exists
2. Verify write permissions
3. Check disk space
