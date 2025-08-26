# syntax=docker/dockerfile:1.7
# Tiny production image using python:alpine and multi-stage to minimize size

FROM --platform=$BUILDPLATFORM python:3.12-alpine AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Build stage to compile wheels (ensures smallest runtime)
FROM base AS builder
WORKDIR /w
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

# Final runtime stage
FROM --platform=$TARGETPLATFORM python:3.12-alpine AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Copy app code
COPY app ./app
COPY wsgi.py ./wsgi.py

# Create non-root user
RUN addgroup -S app && adduser -S app -G app
USER app

EXPOSE 8000

# Healthcheck
HEALTHCHECK CMD wget -qO- http://127.0.0.1:8000/ >/dev/null 2>&1 || exit 1

# Use gunicorn as server (1 worker is enough for this tiny app)
CMD ["gunicorn", "-b", "0.0.0.0:8000", "wsgi:app", "--workers", "1", "--threads", "2"]
