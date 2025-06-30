# database_utils.py

import sqlite3
import pandas as pd
import pickle
import os
from tkinter import messagebox

#import the shared variables
import shared_state

# --- DATABASE AND FILE CONSTANTS ---
DB_FILE = 'attendance.db'
ENCODINGS_PATH = 'known_face_encodings.pkl'

### --- DATABASE FUNCTIONS --- ###
def db_connect():
    return sqlite3.connect(DB_FILE)

def setup_database():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS students (roll_no TEXT PRIMARY KEY, name TEXT NOT NULL, branch TEXT, year TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS professors (prof_id TEXT PRIMARY KEY, name TEXT NOT NULL, department TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS schedule (period_id INTEGER PRIMARY KEY, period_name TEXT, start_time TEXT, end_time TEXT, prof_id TEXT, prof_name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS attendance_logs (log_id INTEGER PRIMARY KEY, student_roll_no TEXT, student_name TEXT, period_name TEXT, prof_name TEXT, timestamp DATETIME)")
    conn.commit()
    conn.close()
    print("Database setup verified.")

def load_all_data_from_db():
    try:
        conn = db_connect()
        shared_state.student_details_df = pd.read_sql_query("SELECT * FROM students", conn).set_index('roll_no', drop=False)
        shared_state.professor_details_df = pd.read_sql_query("SELECT * FROM professors", conn).set_index('prof_id', drop=False)
        shared_state.SCHEDULED_PERIODS = pd.read_sql_query("SELECT * FROM schedule", conn).to_dict('records')
        conn.close()
        print(f"Loaded {len(shared_state.student_details_df)} students, {len(shared_state.professor_details_df)} profs, {len(shared_state.SCHEDULED_PERIODS)} periods.")
    except Exception as e:
        print(f"DB Load Error: {e}")

    if os.path.exists(ENCODINGS_PATH):
        try:
            with open(ENCODINGS_PATH, 'rb') as f:
                data = pickle.load(f)
                shared_state.known_face_encodings = data['encodings']
                shared_state.known_face_roll_numbers = [str(rn).strip() for rn in data['roll_numbers']]
        except:
            shared_state.known_face_encodings, shared_state.known_face_roll_numbers = [], []

def log_attendance_db(roll_no, name, period_name, prof_name):
    from datetime import datetime
    try:
        conn = db_connect(); cursor = conn.cursor(); now = datetime.now(); today_str = now.strftime("%Y-%m-%d")
        cursor.execute("SELECT 1 FROM attendance_logs WHERE student_roll_no = ? AND period_name = ? AND date(timestamp) = ?", (roll_no, period_name, today_str))
        if cursor.fetchone(): return False
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO attendance_logs (student_roll_no, student_name, period_name, prof_name, timestamp) VALUES (?, ?, ?, ?, ?)", (roll_no, name, period_name, prof_name, timestamp_str))
        conn.commit(); conn.close(); print(f"DB Log: {name} for {period_name}")
        return True
    except Exception as e:
        print(f"DB Log Error: {e}"); return False

def add_new_student_db(roll_no, name, branch, year):
    try:
        conn = db_connect(); cursor = conn.cursor()
        cursor.execute("INSERT INTO students (roll_no, name, branch, year) VALUES (?, ?, ?, ?)", (roll_no.strip(), name.strip(), branch.strip(), year.strip()))
        conn.commit(); conn.close(); load_all_data_from_db()
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"Student with Roll No {roll_no} already exists."); return False
    except Exception as e:
        messagebox.showerror("DB Error", f"Could not save student: {e}"); return False

def save_new_face_encoding(roll_no, encoding):
    shared_state.known_face_encodings.append(encoding)
    shared_state.known_face_roll_numbers.append(str(roll_no).strip())
    with open(ENCODINGS_PATH, 'wb') as f:
        pickle.dump({'encodings': shared_state.known_face_encodings, 'roll_numbers': shared_state.known_face_roll_numbers}, f)
    return True