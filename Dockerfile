FROM python:3.11-slim

WORKDIR /app

# Set default port
ENV PORT=5000

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn with eventlet for WebSocket support
RUN pip install --no-cache-dir gunicorn eventlet

# Copy application files
COPY . .

# Expose port
EXPOSE $PORT

# Run with gunicorn for production (1 worker for faster startup)
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app
