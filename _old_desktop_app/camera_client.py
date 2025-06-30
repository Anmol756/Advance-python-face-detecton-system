# camera_client.py

import cv2
import face_recognition
import numpy as np
import pickle
import os
import requests  # The new library for sending web requests
import time

# --- CONFIGURATION ---
ENCODINGS_PATH = 'known_face_encodings.pkl'
API_URL = "http://127.0.0.1:5000/api/log_attendance" # The URL of our Flask API
COOLDOWN_PERIOD = 30  # Seconds to wait before logging the same person again

# --- Load Face Encodings ---
def load_encodings():
    print("Loading known face encodings...")
    if os.path.exists(ENCODINGS_PATH):
        with open(ENCODINGS_PATH, 'rb') as f:
            data = pickle.load(f)
            return data['encodings'], data['roll_numbers']
    else:
        print(f"Error: Encodings file not found at {ENCODINGS_PATH}")
        return [], []

def run_camera_client():
    known_face_encodings, known_face_roll_numbers = load_encodings()

    if not known_face_encodings:
        print("No faces enrolled. Please run the desktop app to enroll faces first.")
        return

    # Dictionary to keep track of the last time a person was logged
    last_logged_time = {}

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Camera client started. Looking for faces...")
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            roll_no = "Unknown"
            
            if len(distances) > 0 and np.min(distances) < 0.6:
                best_match_index = np.argmin(distances)
                roll_no = known_face_roll_numbers[best_match_index]

                # --- The Core Logic Change is Here ---
                current_time = time.time()
                
                # Check if this person was logged recently
                if roll_no not in last_logged_time or (current_time - last_logged_time[roll_no]) > COOLDOWN_PERIOD:
                    print(f"Recognized {roll_no}. Sending to server...")
                    
                    try:
                        # Send the roll number to our Flask API
                        payload = {'roll_no': roll_no}
                        response = requests.post(API_URL, json=payload, timeout=5)
                        
                        # Print the server's response
                        print(f"Server response: {response.json()}")
                        
                        # Update the last logged time for this person
                        last_logged_time[roll_no] = current_time
                        
                    except requests.exceptions.RequestException as e:
                        print(f"API Error: Could not connect to server. Is it running? Error: {e}")

            # --- Display logic for the camera window ---
            top, right, bottom, left = [v * 4 for v in face_location]
            box_color = (0, 255, 0) if roll_no != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
            cv2.putText(frame, str(roll_no), (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        cv2.imshow('Camera Client', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    run_camera_client()