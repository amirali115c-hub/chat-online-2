# ChatOnline - Production Deployment Guide

## Quick Start (Local Development)

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Set Environment Variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run the Application**
```bash
python app.py
# Or with gunicorn for production:
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

4. **Access the App**
Open http://localhost:5000 in your browser

## Production Deployment Options

### Option 1: Heroku
```bash
heroku create your-chatonline-app
git push heroku main
```

### Option 2: Render
1. Connect your GitHub repository to Render
2. Add a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`

### Option 3: Docker
```bash
docker build -t chatonline .
docker run -p 5000:5000 chatonline
```

### Option 4: VPS (Ubuntu)
```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip nginx postgresql

# Clone and setup
git clone your-repo
cd chatonline
pip install -r requirements.txt

# Setup systemd service
sudo nano /etc/systemd/system/chatonline.service
# [Unit] Section and [Service] configuration

# Enable and start
sudo systemctl enable chatonline
sudo systemctl start chatonline
```

## Features

- Real-time chat with Socket.IO
- User registration and login
- Public chat rooms
- Private messaging
- Friend requests
- Random chat (like Chatroulette)
- Dating channels
- Content moderation
- Rate limiting
- Mobile responsive design

## Project Structure

```
chatonline/
├── app.py              # Main Flask application
├── api_routes.py       # API endpoints
├── database.py         # Database operations
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── content/            # Blog content
├── data/               # Data files
└── requirements.txt    # Python dependencies
```

## Configuration

Edit `.env` file for:
- Secret keys
- Database connection
- Email settings
- Server port

## Support

For issues or questions, please contact support.
