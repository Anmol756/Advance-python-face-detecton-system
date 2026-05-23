"""
Database schema initialization and migration logic.
Replaces both database_setup.py and the inline init_db() from app.py.
"""
import sqlite3
from werkzeug.security import generate_password_hash

from app.extensions import db_connect


def init_db():
    """Creates all database tables and seeds default data if needed."""
    conn = db_connect()
    cursor = conn.cursor()

    # --- Users Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('admin', 'professor'))
    );
    """)

    # Create default admin and professor users if no users exist
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ('admin', generate_password_hash('adminpass'), 'admin')
            )
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ('professor1', generate_password_hash('profpass'), 'professor')
            )
            conn.commit()
            print("Default admin and professor users created.")
    except Exception as e:
        print(f"Error creating default users: {e}")

    # --- Students Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        roll_no TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        branch TEXT,
        semester INTEGER,
        admission_year INTEGER,
        subject TEXT,
        face_encoding BLOB,
        gender TEXT,
        age INTEGER
    );
    """)

    # Migration: Add gender column if missing
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN gender TEXT;")
        print("Added 'gender' column to 'students' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            print(f"Error adding 'gender' column: {e}")

    # Migration: Add age column if missing
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN age INTEGER;")
        print("Added 'age' column to 'students' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            print(f"Error adding 'age' column: {e}")

    # --- Professors Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS professors (
        prof_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT,
        email TEXT,
        mobile TEXT,
        qualification TEXT,
        experience TEXT,
        achievements TEXT,
        others TEXT,
        photo_data TEXT
    );
    """)

    # --- Schedule Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedule (
        period_id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_name TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        prof_id TEXT,
        prof_name TEXT,
        description TEXT,
        branch TEXT,
        semester INTEGER,
        FOREIGN KEY (prof_id) REFERENCES professors (prof_id)
    );
    """)

    # Migration: Add semester column to schedule if missing
    try:
        cursor.execute("ALTER TABLE schedule ADD COLUMN semester INTEGER;")
        print("Added 'semester' column to 'schedule' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            print(f"Error adding 'semester' column: {e}")

    # --- Attendance Logs Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_roll_no TEXT NOT NULL,
        student_name TEXT,
        period_name TEXT NOT NULL,
        prof_name TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_roll_no) REFERENCES students (roll_no)
    );
    """)

    conn.commit()
    conn.close()
    print("Database tables created/verified successfully.")
