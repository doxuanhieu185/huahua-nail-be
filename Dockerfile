# Multi-stage build for Django backend
FROM python:3.8-alpine AS base

# Install system dependencies
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
    tk-dev \
    tcl-dev \
    tzdata \
    mariadb-dev \
    pkgconfig \
    && rm -rf /var/cache/apk/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip setuptools wheel

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

WORKDIR /code

# Copy requirements first for better caching
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /code/

# Create necessary directories and set permissions
RUN mkdir -p /code/static /code/media && \
    chown -R appuser:appgroup /code

# Switch to non-root user
USER appuser

# Collect static files
# RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health/', timeout=10)" || exit 1

EXPOSE 8000

# Use Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "nail_salon.wsgi:application"]