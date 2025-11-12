# ----------------------------------------------------------------------
# STAGE 1: Build the Frontend (React) Assets
# This stage uses a Node image to build the static files.
# ----------------------------------------------------------------------
FROM node:18-alpine AS frontend-builder

# Set the working directory for the client/frontend
WORKDIR /app/frontend

# Copy package files and install dependencies
COPY ./frontend/package.json ./frontend/package-lock.json ./

# Use --frozen-lockfile or npm ci to ensure repeatable builds
RUN npm ci

# Copy the rest of the frontend source code
COPY ./frontend/ ./

# Run the build command
# This creates the optimized static files (e.g., in a 'build' directory)
RUN npm run build


# ----------------------------------------------------------------------
# STAGE 2: Final Image for Server (Django + Static Assets)
# This stage uses a lightweight Python image for the final runtime.
# ----------------------------------------------------------------------
FROM python:3.11-slim AS final

# Set environment variables for production
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV production
ENV PATH="/py/bin:$PATH"

# Create a non-root user and set up necessary directories
RUN useradd --no-create-home appuser
WORKDIR /usr/src/app

# Install Python dependencies
# Set up a virtual environment and install dependencies
COPY requirements.txt .
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install --no-cache-dir -r requirements.txt && \
    /py/bin/pip install gunicorn

# Copy all Django/Python source code
COPY . .

# Copy built frontend assets from the builder stage
# Assuming your React build output is in 'frontend/build'
COPY --from=frontend-builder /app/frontend/build /usr/src/app/frontend/build

# Collect static files (if using Django's static file serving)
# Adjust if your STATIC_ROOT is different in settings.py
RUN /py/bin/python manage.py collectstatic --noinput

# Expose the default port for Django/Gunicorn
EXPOSE 8000

# Run the application using Gunicorn (recommended production server)
# Ensure manage.py is at the root and replace 'your_project_name' with your actual Django project folder name
CMD ["/py/bin/gunicorn", "--bind", "0.0.0.0:8000", "your_project_name.wsgi:application"]

# Switch to the non-root user for security
USER appuser