# --- Stage 1: Build Frontend ---
FROM node:18 AS build-stage

WORKDIR /app/frontend

COPY ./frontend/package*.json ./
RUN npm ci

COPY ./frontend/ ./

# Accept API_URL as a build argument
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

RUN npm run build

# --- Stage 2: Backend & Final Image ---
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if any)
# RUN apt-get update && apt-get install -y ...

# Install Python dependencies
COPY ./api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend project directory
COPY . .

# Copy the build output from the previous stage
COPY --from=build-stage /app/frontend/build /app/staticfiles

# Expose the port the app runs on
EXPOSE 8000

# --- IMPORTANT ---
# You must:
# 1. Add 'gunicorn' to your requirements.txt
# 2. Change 'your_project_name' to your actual Django project's name
# 3. Make sure your Django settings.py has: STATIC_ROOT = BASE_DIR / "staticfiles"
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "your_project_name.wsgi:application"]