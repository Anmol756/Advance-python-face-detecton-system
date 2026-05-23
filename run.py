"""
Entry point to run the Smart Attendance System Flask application.
Imports the application factory, creates the app, and runs it with SocketIO.
"""
from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    print("Starting Flask-SocketIO server on http://127.0.0.1:5000")
    # Setting allow_unsafe_werkzeug=True is required when running locally on some environments
    socketio.run(app, debug=True, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)
