# ----------------------------------------------------------------------
# STAGE 1: Build the Frontend (React) Assets
# ----------------------------------------------------------------------
FROM node:18-alpine AS frontend-builder

# Set the working directory for the client/frontend
WORKDIR /app/frontend

# Copy package files and install dependencies
COPY ./frontend/package.json ./frontend/package-lock.json ./

# Use npm ci for repeatable dependency installation
RUN npm ci

# Copy the rest of the frontend source code
COPY ./frontend/ ./

# Run the production build command
RUN npm run build


# ----------------------------------------------------------------------
# STAGE 2: Final Image for Server (Django + Static Assets)
# ----------------------------------------------------------------------
FROM python:3.11-slim AS final

# Define the build argument for the secret key
# This ARG will be set by your GitHub Action 'build-args'
ARG DJANGO_SECRET_KEY

# Set general environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV production
ENV PATH="/py/bin:$PATH"

# Create a non-root user and set up necessary directories
RUN useradd --no-create-home appuser
WORKDIR /usr/src/app

# Install Python dependencies
COPY requirements.txt .
# Set up a virtual environment and install dependencies, including gunicorn
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install --no-cache-dir -r requirements.txt && \
    /py/bin/pip install gunicorn

# Copy all Django/Python source code
COPY . .

# Copy built frontend assets from the builder stage
# Assumes 'frontend/build' is the output folder
COPY --from=frontend-builder /app/frontend/build /usr/src/app/frontend/build

# Collect static files
# CRITICAL FIX: Pass the DJANGO_SECRET_KEY into the environment only for the collectstatic command
RUN DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY} /py/bin/python manage.py collectstatic --noinput

# Expose the default port
EXPOSE 8000

# Run the application using Gunicorn
# IMPORTANT: Replace 'your_project_name' with your actual Django project folder name
CMD ["/py/bin/gunicorn", "--bind", "0.0.0.0:8000", "your_project_name.wsgi:application"]

# Switch to the non-root user for security
USER appuser