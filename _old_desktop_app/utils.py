# utils.py

import os
import sys

# This file should only contain general-purpose helper functions
# that don't depend on other parts of our application.

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def play_sound(sound_path):
    """Plays a sound file if it exists."""
    if not os.path.exists(sound_path):
        print(f"Warning: Sound file not found at '{sound_path}'.")
        return
    try:
        import simpleaudio as sa
        wave_obj = sa.WaveObject.from_wave_file(sound_path)
        wave_obj.play()
    except Exception as e:
        print(f"Sound Error: {e}")

# Define the path using the function so other modules can import it
SUCCESS_SOUND_PATH = resource_path(os.path.join('sounds', 'success.wav'))