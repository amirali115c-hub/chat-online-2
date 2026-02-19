# Chat Online - Important Details

## Project Overview
- **Project:** Chat Online - 18+ Chat Platform
- **Repository:** https://github.com/amirali115c-hub/chat-online-2
- **Deployment:** Koyeb (auto-deploys from GitHub)
- **Koyeb URL:** https://youngest-jacinda-chatonlline-0c291dbf.koyeb.app/

---

## Amir's Copywriting Checklist

**CRITICAL:** Before writing ANY blog post for Amir, read:
- `memory/amir-copywriting-blog-checklist.md` (MANDATORY)
- `memory/amir-complete-writing-checklist.md`
- `memory/amir-writing-soul-strict.md`
- `memory/ultimate-seo-content-mastery-prompt.md`

**Key Rules:**
- ❌ NEVER use em dash (—)
- ✅ Word count: 2000-3000 words minimum
- ✅ Include: Meta title, Meta description, URL slug
- ✅ Include: Introduction, FAQ section, Conclusion, About the Author
- ✅ 95%+ contractions
- ✅ Personal experience ("I have seen", "I have talked to")
- ✅ Honest frustration, simple contrasts, fragments for impact
- ❌ No formal connectors ("Despite", "Nevertheless", "Furthermore", "Moreover")

---

## Admin Panel Credentials

### Local Development
- **URL:** http://127.0.0.1:5000/admin
- **Username:** `admin`
- **Password:** `SecureP@ssw0rd2024!`

### Koyeb/Production
- **URL:** https://youngest-jacinda-chatonlline-0c291dbf.koyeb.app/admin
- **Username:** `admin`
- **Password:** (Set in Koyeb environment variables as `ADMIN_PASSWORD`)

---

## Environment Variables

### Required for Production (.env file or Koyeb)

| Variable | Value | Purpose |
|----------|-------|---------|
| `SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` | Flask session secret |
| `JWT_SECRET` | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` | JWT token signing |
| `ADMIN_USERNAME` | `admin` | Admin login username |
| `ADMIN_PASSWORD` | (your secure password) | Admin login password |
| `DATABASE_URL` | `sqlite:///chat_online.db` (dev) or PostgreSQL URL (prod) | Database connection |
| `FLASK_ENV` | `development` or `production` | Environment mode |

---

## Installed Dependencies

```bash
Flask>=2.3.0
Flask-SocketIO>=5.3.0
Flask-SQLAlchemy>=3.0.0
python-socketio>=5.9.0
eventlet>=0.33.0
PyJWT>=2.8.0
Werkzeug>=2.3.0
gunicorn>=21.0.0
python-dotenv>=1.0.0
psycopg2-binary>=2.9.0
sentry-sdk>=1.40.0
markdown>=3.0.0
```

---

## Key Routes

| Route | Purpose |
|-------|---------|
| `/` | Homepage |
| `/welcome` | After login |
| `/admin` | Admin dashboard |
| `/admin/health` | Health monitoring |
| `/admin/blog` | Blog management |
| `/admin/blog/new` | Create blog post |
| `/admin/upload` | Upload images |
| `/blog/[slug]` | View blog post |
| `/api/health` | Health check API |
| `/api/debug/connections` | Debug connections |

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/login` | POST | User login |
| `/api/register` | POST | User registration |
| `/api/online/all` | GET | All online users |
| `/api/health` | GET | Health status |
| `/api/debug/connections` | GET | Debug connection issues |
| `/api/admin/login` | POST | Admin login |
| `/api/log-error` | POST | Log client errors |

---

## Features Implemented

### Completed
- [x] User registration and login
- [x] Guest chat (no registration required)
- [x] Real-time chat with Socket.IO
- [x] Chat rooms
- [x] Random chat matching
- [x] Private messaging
- [x] Friend system
- [x] Blog with Markdown support
- [x] Image uploads
- [x] Age verification modal
- [x] SEO meta tags
- [x] Health monitoring dashboard
- [x] Rate limiting
- [x] Admin authentication
- [x] Comprehensive logging

### In Progress
- [ ] Email verification
- [ ] Password reset
- [ ] User blocking
- [ ] Reporting system

---

## Issues Fixed

1. **Online Users List** - Fixed socket connection tracking for guests
2. **Inconsistent Icons** - Changed to `fa-comment-dots` for consistency
3. **Age Modal Flash** - Hidden by default, shown only when needed
4. **Socket Disconnects** - Added heartbeat and stale connection cleanup

---

## Log File Location
- **Local:** `logs/chat-online.log`
- **Koyeb:** View in Koyeb dashboard logs

---

## Daily Tasks (To Remind)

1. **Check admin health dashboard** (`/admin/health`)
2. **Check for errors** in `logs/chat-online.log`
3. **Review analytics** - popular pages, page views
4. **Monitor online users** count
5. **Check for broken links** (404 errors)

---

## Weekly Tasks

1. **Backup database** (SQLite: copy `chat_online.db`)
2. **Review error logs**
3. **Add new blog posts**
4. **Update FAQ if needed**
5. **Check user feedback**

---

## Troubleshooting

### Issue: "No users online" when you are online
**Fix:** Check `/api/debug/connections` - socket may not be connecting properly

### Issue: Admin panel returns 401
**Fix:** Login at `/admin` first with credentials

### Issue: Rate limited
**Fix:** Wait 1 hour, or check `/api/health/errors`

### Issue: Database errors
**Fix:** Check `logs/chat-online.log` for details

---

## To-Do Reminder (Tomorrow)

1. [ ] Check Koyeb deployment status
2. [ ] Test admin login on production
3. [ ] Test online users list
4. [ ] Add 2-3 new blog posts
5. [ ] Configure Sentry for error tracking (optional)
6. [ ] Set up PostgreSQL for production (optional)
