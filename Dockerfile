FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn with eventlet for WebSocket support
RUN pip install --no-cache-dir gunicorn eventlet

# Copy application files
COPY . .

# Expose port
EXPOSE $PORT

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
