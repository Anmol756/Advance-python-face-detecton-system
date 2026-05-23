"""
Flask Application Factory.
Initializes Flask app, registers blueprints, hooks extensions (SocketIO), and loads face encodings.
"""
from flask import Flask
import os
import config
from app.extensions import socketio, load_face_encodings, close_connection
from app.models import init_db

def create_app():
    # Since static is at the root level and app/ is the package,
    # we point static_folder to the root static directory.
    app = Flask(
        __name__,
        static_folder='../static',
        static_url_path='/static',
        template_folder='templates'
    )
    
    # Load configuration from config.py module
    app.config.from_object(config)
    
    # Register app context teardown to close DB connections
    app.teardown_appcontext(close_connection)
    
    # Initialize DB (creates tables and migrations if needed)
    with app.app_context():
        init_db()
        load_face_encodings()

    # Import blueprints and register them
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.students.routes import students_bp
    from app.professors.routes import professors_bp
    from app.schedule.routes import schedule_bp
    from app.attendance.routes import attendance_bp, register_socketio_handlers

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(professors_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(attendance_bp)

    # Initialize extensions
    socketio.init_app(app)
    register_socketio_handlers(socketio)

    return app
