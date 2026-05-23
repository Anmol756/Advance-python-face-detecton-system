# ==========================================
# Stage 1: Build stage (compiles dependencies)
# ==========================================
FROM python:3.10-slim AS builder

WORKDIR /build

# Install compiler tools and libraries needed to compile Dlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    pkg-config \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set compiler flag to restrict build to a single core. 
# This prevents out-of-memory errors on small VMs during compilation of heavy templates (e.g. dlib).
ENV MAKEFLAGS="-j1"

# Copy requirements manifest
COPY requirements.txt .

# Pre-compile wheels for all requirements to avoid compilation in the final container
RUN pip wheel --no-cache-dir --wheel-dir=/build/wheels -r requirements.txt


# ==========================================
# Stage 2: Final lightweight runner stage
# ==========================================
FROM python:3.10-slim

WORKDIR /app

# Install runtime-only requirements for OpenCV, MediaPipe, and Dlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas3 \
    liblapack3 \
    libgl1 \
    libglx-mesa0 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-compiled wheels from builder stage and install
COPY --from=builder /build/wheels /wheels
COPY requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt && rm -rf /wheels

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
