# syntax=docker/dockerfile:1.7
# Single-stage build for ARM64 to avoid cross-platform dependency issues

FROM --platform=$TARGETPLATFORM python:3.12-alpine
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies and Python packages in one layer
RUN apk add --no-cache gcc musl-dev linux-headers && \
    pip install --no-cache-dir flask==3.0.3 gunicorn==22.0.0 && \
    apk del gcc musl-dev linux-headers

# Copy app code
COPY app ./app
COPY wsgi.py ./wsgi.py

# Create non-root user
RUN addgroup -S app && adduser -S app -G app
USER app

EXPOSE 8000

# Healthcheck
HEALTHCHECK CMD wget -qO- http://127.0.0.1:8000/ >/dev/null 2>&1 || exit 1

# Use gunicorn as server
CMD ["gunicorn", "-b", "0.0.0.0:8000", "wsgi:app", "--workers", "1", "--threads", "2"]
