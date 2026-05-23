"""
Centralized configuration for the Smart Attendance System.
All configurable values are defined here instead of being scattered across app.py.
"""
import os

# --- Base Directory ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# --- Flask Core ---
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'a_default_super_secret_key_that_should_be_changed_2025')
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_NAME = 'my_attendance_session'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_SAMESITE = 'Lax'

# --- Database ---
DB_FILE = os.path.join(BASE_DIR, 'attendance.db')
ENCODINGS_PATH = os.path.join(BASE_DIR, 'known_face_encodings.pkl')

# --- Timezone ---
TIMEZONE = 'Asia/Kolkata'

# --- User Roles ---
ADMIN_ROLE = 'admin'
PROFESSOR_ROLE = 'professor'

# --- Face Recognition ---
CONFIDENCE_THRESHOLD = 0.5
COOLDOWN_PERIOD = 30          # Seconds before a student can be logged again
AGE_MOOD_COOLDOWN_PERIOD = 5  # Seconds between age/mood detection runs

# --- Liveness Detection ---
EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 3
LIVENESS_CHECK_COOLDOWN = 3
LIVENESS_SCALE_FACTOR = 0.25

# --- ML Model Paths ---
MODEL_DIR = os.path.join(BASE_DIR, 'models')
AGE_MODEL_PROTO = os.path.join(MODEL_DIR, 'deploy_age.prototxt')
AGE_MODEL_CAFFE = os.path.join(MODEL_DIR, 'age_net.caffemodel')
GENDER_MODEL_PROTO = os.path.join(MODEL_DIR, 'deploy_gender.prototxt')
GENDER_MODEL_CAFFE = os.path.join(MODEL_DIR, 'gender_net.caffemodel')
EMOTION_MODEL_PROTO = os.path.join(MODEL_DIR, 'deploy_emotion.prototxt')
EMOTION_MODEL_CAFFE = os.path.join(MODEL_DIR, 'emotion_net.caffemodel')
LANDMARKS_MODEL_PATH = os.path.join(MODEL_DIR, 'shape_predictor_68_face_landmarks.dat')

# --- ML Labels ---
AGE_BUCKETS = [
    "(0-2)", "(4-6)", "(8-12)", "(15-18)", "(18-22)",
    "(22-25)", "(25-32)", "(38-43)", "(48-53)", "(60-100)"
]
GENDER_LIST = ['Male', 'Female']
EMOTION_LIST = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
