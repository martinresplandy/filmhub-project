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

# CRITICAL FIX: Accepter le nouvel ARGUMENT injecté par le CD
ARG API_URL_BUILD
ARG CACHE_BREAKER=default-value

# CRITICAL FIX: Convertir l'ARG en ENV pour le processus de construction
ENV REACT_APP_API_URL=$API_URL_BUILD

# Build the React application
# Le processus npm run build lira maintenant la variable d'environnement REACT_APP_API_URL
RUN npm run build

# ===============================================================
# --- Stage 2: Install Python Dependencies (python:3.11-slim) ---
# ===============================================================
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
ENV DJANGO_SETTINGS_MODULE=filmhub.settings

# Set WORKDIR to /app (Standard Django root)
WORKDIR /app 

# 1. Copy installed dependencies from the builder stage
COPY --from=backend-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-deps /usr/local/bin/gunicorn /usr/local/bin/

# 2. Copy the necessary backend source code based on your project schema:
COPY ./api/ /app/api/ 
COPY manage.py /app/
COPY filmhub/ /app/filmhub/
COPY docker-entrypoint.sh /app/

# 3. Copy the compiled frontend assets (React build)
COPY --from=frontend-build /app/frontend/build /app/static 

# 4. Set executable permissions for the entrypoint script
RUN chmod +x /app/docker-entrypoint.sh

# Expose the port Gunicorn runs on
EXPOSE 8000

# Set the entrypoint to the custom script
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# The default command to run 
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "filmhub.wsgi:application"]