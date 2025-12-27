# Multi-stage build for Django backend
<<<<<<< HEAD
FROM python:3.11-alpine AS builder

# Install build dependencies
=======
FROM python:3.8-alpine AS base

# Install system dependencies
>>>>>>> 869736e606aa35ec4f68d40b7f667e05aa8f68ef
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
<<<<<<< HEAD
    mariadb-dev \
    pkgconfig

# Upgrade pip and install wheel
RUN pip install --upgrade pip setuptools wheel

# Copy and install requirements
COPY requirements.txt /tmp/
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /tmp/wheels -r /tmp/requirements.txt

# Production stage
FROM python:3.11-alpine AS production

# Install runtime dependencies only
RUN apk add --no-cache \
    jpeg \
    zlib \
    freetype \
    lcms2 \
    openjpeg \
    tiff \
    mariadb-connector-c \
    tzdata \
    && rm -rf /var/cache/apk/*

=======
    tk-dev \
    tcl-dev \
    tzdata \
    mariadb-dev \
    pkgconfig \
    && rm -rf /var/cache/apk/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip setuptools wheel

>>>>>>> 869736e606aa35ec4f68d40b7f667e05aa8f68ef
# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

<<<<<<< HEAD
# Copy wheels and install
COPY --from=builder /tmp/wheels /wheels
RUN pip install --no-cache /wheels/*

WORKDIR /app

# Copy application code
COPY --chown=appuser:appgroup . /app/

# Create directories for static and media files
RUN mkdir -p /app/static /app/media && \
    chown -R appuser:appgroup /app
=======
WORKDIR /code

# Copy requirements first for better caching
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /code/

# Create necessary directories and set permissions
RUN mkdir -p /code/static /code/media && \
    chown -R appuser:appgroup /code
>>>>>>> 869736e606aa35ec4f68d40b7f667e05aa8f68ef

# Switch to non-root user
USER appuser

<<<<<<< HEAD
# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/admin/', timeout=10)" || exit 1
=======
# Collect static files
# RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health/', timeout=10)" || exit 1
>>>>>>> 869736e606aa35ec4f68d40b7f667e05aa8f68ef

EXPOSE 8000

# Use Gunicorn for production
<<<<<<< HEAD
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "nail_salon.wsgi:application"]
=======
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "nail_salon.wsgi:application"]
>>>>>>> 869736e606aa35ec4f68d40b7f667e05aa8f68ef
