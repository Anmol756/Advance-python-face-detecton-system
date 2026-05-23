"""
Face processing utilities — encoding, liveness detection, ML model loading.
Extracted from app.py to keep face recognition logic isolated.
"""
import os
import base64
import time
from io import BytesIO

import cv2
import numpy as np
import face_recognition
import dlib
from scipy.spatial import distance as dist
from flask import flash

import config


# --- Dlib Predictor (For blink/liveness detection) ---
predictor = None

try:
    if os.path.exists(config.LANDMARKS_MODEL_PATH):
        predictor = dlib.shape_predictor(config.LANDMARKS_MODEL_PATH)
        print("Dlib shape predictor loaded successfully.")
    else:
        print(f"Dlib shape predictor not found at {config.LANDMARKS_MODEL_PATH}. Liveness detection will not work.")
except Exception as e:
    print(f"Error loading Dlib shape predictor: {e}. Liveness detection will not work.")
    predictor = None


# --- Utility Functions ---

def eye_aspect_ratio(eye):
    """Calculates the Eye Aspect Ratio (EAR) for blink detection."""
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear


def process_and_encode(image_stream):
    """
    Reads an image from a file-like object, detects a face, and returns its encoding.
    Returns None if no face is found or encoding fails.
    """
    try:
        image_bytes = image_stream.read()
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            flash("Could not decode the uploaded image. Please try a different file.", "danger")
            return None

        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_img, model="hog")
        if not face_locations:
            flash("No face detected in the uploaded image. Please upload a clear photo with a visible face.", "danger")
            return None

        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        if not face_encodings:
            flash("Could not extract face encoding. Please try a different photo.", "danger")
            return None

        return face_encodings[0]
    except Exception as e:
        print(f"Exception in process_and_encode: {e}")
        flash(f"Error processing image for face encoding: {e}", "danger")
        return None


def image_to_base64(image_stream):
    """Reads an image from a file-like object and converts it to a base64 string."""
    try:
        image_bytes = image_stream.read()
        return base64.b64encode(image_bytes).decode('utf-8')
    except Exception as e:
        print(f"Error converting image to base64: {e}")
        return None
