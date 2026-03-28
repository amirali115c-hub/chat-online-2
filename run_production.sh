#!/usr/bin/env bash
# Run chatonline with eventlet (production mode)
# Usage: ./run_production.sh

cd "$(dirname "$0")"

# Load environment
set -a
[ -f .env ] && source .env
set +a

# Must be before ANY imports
python3 -c "import eventlet; eventlet.monkey_patch()"

# Now run with eventlet
python3 -c "
import eventlet
eventlet.monkey_patch()

from app import app, socketio

socketio.run(
    app,
    debug=False,
    port=int('$PORT' or 5001),
    host='0.0.0.0',
)
"
