import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-26w936$xdpc-v#_2@$@x+^0mgz!lpp-r^)2dr@959df5gv(4jl"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
if DEBUG:
    ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',
    'rest_framework.authtoken',  # Para autenticação com Token
    'api',
    'corsheaders',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = "filmhub.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'staticfiles'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "filmhub.wsgi.application"

DB_HOST_RENDER = os.environ.get('DB_HOST')

IS_CI = os.environ.get('CI_ENVIRONMENT', 'False').lower() == 'true'

if DB_HOST_RENDER:
    # 1. Production (Render)
    DB_HOST = DB_HOST_RENDER
elif IS_CI:
    DB_HOST = os.environ.get('CI_DB_HOST', 'localhost') 
    DB_NAME_CI = os.environ.get('CI_DB_NAME', 'test_db')
    DB_USER_CI = os.environ.get('CI_DB_USER', 'runner') 
    DB_PASSWORD_CI = os.environ.get('CI_DB_PASSWORD', 'password')
else:
    raise ValueError("Database host environment variable is not configured!")


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': DB_HOST, 
        'NAME': os.environ.get('DB_NAME') if DB_HOST_RENDER else DB_NAME_CI,
        'USER': os.environ.get('DB_USER') if DB_HOST_RENDER else DB_USER_CI,
        'PASSWORD': os.environ.get('DB_PASSWORD') if DB_HOST_RENDER else DB_PASSWORD_CI,
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Check to prevent running with incomplete settings if needed:
if os.environ.get('DEBUG') == 'False' and not os.environ.get('DB_HOST'):
    raise ValueError("DB_HOST environment variable is not set for production!")


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework - Token authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')

if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "https://filmhub-frontend-n6i3.onrender.com",
    ]
    CORS_ALLOW_ALL_ORIGINS = True