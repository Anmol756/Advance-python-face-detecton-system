import os
from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    # Read host, port, and debug from environment variables
    # Default host is 0.0.0.0 for Docker routing, default port is 5000
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    
    print(f"Starting Flask-SocketIO server on http://{host}:{port} (debug={debug})")
    # Setting allow_unsafe_werkzeug=True is required when running locally on some environments
    socketio.run(app, debug=debug, host=host, port=port, allow_unsafe_werkzeug=True)
