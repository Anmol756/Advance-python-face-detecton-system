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

# Install precompiled dlib-bin first so it satisfies the dlib requirement for face-recognition
# This completely bypasses compiling dlib from source, resolving Render's 8GB memory limit crash
RUN pip install --no-cache-dir dlib-bin

# Copy and install the rest of requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (includes code, static elements, and models)
COPY . .

# Expose port (Render overrides this with dynamic PORT variable, default 5000)
EXPOSE 5000

# Set environment defaults
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Run entry point
CMD ["python", "run.py"]
