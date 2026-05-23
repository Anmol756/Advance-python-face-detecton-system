FROM python:3.10-slim

WORKDIR /app

# Install runtime requirements for OpenCV, MediaPipe, and Dlib
# Using development meta-packages (e.g. -dev) ensures compatibility across different Debian versions (Bookworm vs Trixie)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas-dev \
    liblapack-dev \
    libgl1 \
    libglx-mesa0 \
    libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements manifest
COPY requirements.txt .

# Install precompiled dlib-bin and other direct dependencies of face-recognition
RUN pip install --no-cache-dir dlib-bin face-recognition-models pillow

# Filter out dlib and face_recognition from requirements.txt to prevent pip from attempting to compile dlib
RUN grep -ivE "dlib|face_recognition" requirements.txt > temp_reqs.txt
RUN pip install --no-cache-dir -r temp_reqs.txt

# Install face-recognition without pulling its dependencies (dlib is satisfied by dlib-bin)
RUN pip install --no-cache-dir --no-deps face-recognition

# Copy application files (includes code, static elements, and models)
COPY . .

# Expose port (Render overrides this with dynamic PORT variable, default 5000)
EXPOSE 5000

# Set environment defaults
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Run entry point using optimized single-worker Gunicorn and eventlet for low memory
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "--timeout", "120", "run:app"]
