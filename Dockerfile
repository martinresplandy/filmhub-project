# =========================================
# --- Stage 1: Build Frontend (node:18) ---
# =========================================

FROM node:18 AS frontend-build
# Set the working directory inside the container
WORKDIR /app/frontend

# Copy package files and install dependencies (for caching)
COPY ./frontend/package*.json ./
RUN npm ci

# Copy the rest of the frontend source code
COPY ./frontend/ ./

# Accept API_URL as a build argument
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

RUN echo "API URL is set to $REACT_APP_API_URL"

# Build the React application
RUN npm run build

# ===============================================================
# --- Stage 2: Install Python Dependencies (python:3.11-slim) ---
# ===============================================================
# This stage installs system dependencies and Python packages
FROM python:3.11-slim AS backend-deps

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install system dependencies (needed for psycopg2 compilation)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set work directory for Python dependencies
WORKDIR /app

# Copy requirements and install (for caching)
COPY ./api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =======================================
# --- Stage 3: Final Production Image ---
# =======================================
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED 1
# Set Django settings module (filmhub/ is at the root of the app)
ENV DJANGO_SETTINGS_MODULE=filmhub.settings

# CRITICAL FIX 1: Set WORKDIR to /app (Standard Django root)
WORKDIR /app 

# 1. Copy installed dependencies from the builder stage
COPY --from=backend-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-deps /usr/local/bin/gunicorn /usr/local/bin/

# 2. CRITICAL FIX 2: Copy the necessary backend source code based on your project schema:
# Copy the API application module
COPY ./api/ /app/api/ 
# Copy Django configuration folder (filmhub/), manage.py, and docker-entrypoint.sh from the repo root
COPY manage.py /app/
COPY filmhub/ /app/filmhub/
COPY docker-entrypoint.sh /app/

# 3. Copy the compiled frontend assets (React build)
# Destination path /app/static must match STATIC_ROOT in settings.py
COPY --from=frontend-build /app/frontend/build /app/static 

# 4. Set executable permissions for the entrypoint script
RUN chmod +x /app/docker-entrypoint.sh

# Expose the port Gunicorn runs on
EXPOSE 8000

# Set the entrypoint to the custom script
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# The default command to run (will be executed by the entrypoint script)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "filmhub.wsgi:application"]