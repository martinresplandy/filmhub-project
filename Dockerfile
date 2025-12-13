# --- Stage 1: Build Frontend (node:18) ---

FROM node:18 AS frontend-build

WORKDIR /app/frontend

COPY ./frontend/package*.json ./
RUN npm ci

COPY ./frontend/ ./

ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

RUN npm run build

FROM python:3.11-slim AS backend-deps

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

COPY ./api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Production Image ---

FROM python:3.11-slim AS production

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=filmhub.settings

WORKDIR /app

COPY --from=backend-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-deps /usr/local/bin/gunicorn /usr/local/bin/

COPY ./api/ /app/

COPY --from=frontend-build /app/frontend/build /app/build 

COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "filmhub.wsgi:application"]