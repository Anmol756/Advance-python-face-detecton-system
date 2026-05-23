"""
Shared extensions and global state for the Smart Attendance System.
Provides database helpers, SocketIO instance, and face encoding management.
"""
import sqlite3
import pickle
import os

from flask import g
from flask_socketio import SocketIO

import config

# --- SocketIO Instance ---
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

# --- Global Face Encoding State ---
known_face_encodings = []
known_face_roll_numbers = []
last_logged_time = {}        # Cooldown for attendance logging per student
last_age_mood_time = {}      # Cooldown for age/mood detection per face
last_liveness_check_times = {}  # Cooldown for liveness check per face_id (roll_no or unknown_i)

# --- Liveness / Blink Detection State ---
blink_counters = {}             # Blink counter per face_id (roll_no or unknown_i)


# --- Database Helpers ---

def db_connect():
    """Establishes a connection to the SQLite database with row_factory for dict-like access."""
    conn = sqlite3.connect(config.DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    """Returns a request-scoped database connection (stored on Flask's g object)."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(config.DB_FILE, timeout=10)
        db.row_factory = sqlite3.Row
    return db


def close_connection(exception):
    """Teardown function to close the request-scoped database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# --- Face Encoding Persistence ---

def save_face_encodings():
    """Saves the in-memory known_face_encodings and roll_numbers to a pickle file."""
    global known_face_encodings, known_face_roll_numbers
    try:
        with open(config.ENCODINGS_PATH, 'wb') as f:
            pickle.dump({
                'encodings': known_face_encodings,
                'roll_numbers': known_face_roll_numbers
            }, f)
        print("Face encodings saved to file.")
    except Exception as e:
        print(f"Error saving encodings file: {e}")


def load_face_encodings():
    """Loads known face encodings and their associated roll numbers from the database into memory and caches them to pickle."""
    global known_face_encodings, known_face_roll_numbers
    print("Loading known face encodings from database...")
    encs = []
    rns = []
    try:
        with db_connect() as conn:
            students = conn.execute("SELECT roll_no, face_encoding FROM students WHERE face_encoding IS NOT NULL").fetchall()
            for student in students:
                try:
                    encoding = pickle.loads(student['face_encoding'])
                    encs.append(encoding)
                    rns.append(str(student['roll_no']).strip())
                except Exception as e:
                    print(f"Error loading face encoding for student {student['roll_no']}: {e}")
        known_face_encodings = encs
        known_face_roll_numbers = rns
        print(f"Loaded {len(known_face_encodings)} known faces from database.")
        
        # Save back to pickle file cache
        save_face_encodings()
    except Exception as e:
        print(f"Error loading face encodings from database: {e}")
        # Fallback to pickle if database fails
        if os.path.exists(config.ENCODINGS_PATH):
            try:
                with open(config.ENCODINGS_PATH, 'rb') as f:
                    data = pickle.load(f)
                known_face_encodings = data['encodings']
                known_face_roll_numbers = [str(rn).strip() for rn in data['roll_numbers']]
                print(f"Loaded {len(known_face_encodings)} known faces from pickle backup.")
            except Exception as pe:
                print(f"Error loading pickle backup: {pe}")
                known_face_encodings, known_face_roll_numbers = [], []
        else:
            known_face_encodings, known_face_roll_numbers = [], []


# --- Common Query Helpers ---

def get_distinct_from_db(column_name, table_name='students'):
    """Fetches unique values for filter dropdowns from a specified table."""
    try:
        with db_connect() as conn:
            cursor = conn.cursor()
            if column_name in ['semester', 'admission_year']:
                query = f"SELECT DISTINCT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL ORDER BY CAST({column_name} AS INTEGER)"
            else:
                query = f"SELECT DISTINCT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL ORDER BY {column_name}"
            cursor.execute(query)
            return [item[0] for item in cursor.fetchall()]
    except sqlite3.OperationalError as e:
        print(f"DB Error fetching distinct {column_name} from {table_name}: {e}.")
        return []
    except Exception as e:
        print(f"Unexpected error fetching distinct {column_name} from {table_name}: {e}")
        return []
