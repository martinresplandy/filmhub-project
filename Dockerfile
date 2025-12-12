# --- Stage 1: Builder - Installs Python dependencies ---
FROM python:3.11-slim as builder

# Set work directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install Python dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# Copy requirements first to leverage Docker layer caching
COPY ./api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final Production Image ---
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=filmhub.settings

# Set work directory
WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/

COPY . /app/

COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Expose the port Gunicorn runs on
EXPOSE 8000

# Set the entrypoint to the script for robust startup
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# The default command to run when the container starts (executed by the entrypoint script)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "filmhub.wsgi:application"]