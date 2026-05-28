# ============================================================
# InfraPilot Backend Dockerfile
# ============================================================
# Multi-stage build:
# Stage 1 (builder): Install dependencies
# Stage 2 (runtime): Copy only what's needed - smaller image
#
# Why multi-stage?
# - Builder stage can have build tools (gcc, etc.)
# - Runtime stage stays lean and secure
# ============================================================

# Stage 1: Builder
FROM python:3.12-slim AS builder

# Set working directory inside the container
WORKDIR /app

# Install dependencies first (cached by Docker if requirements.txt doesn't change)
# This is a key Docker optimization - don't copy all code before installing deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime image
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY ./app ./app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Expose port (documentation only - actual port mapping is in docker-compose)
EXPOSE 8000

# Health check - Docker will restart the container if this fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run the application
# --host 0.0.0.0 makes it accessible from outside the container
# --workers 1 is fine for development; use more in production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
