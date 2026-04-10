import os
from pathlib import Path
import dj_database_url
import os


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'change-me-nishpa'
DEBUG = True
ALLOWED_HOSTS = [".onrender.com", 'localhost', '127.0.0.1', ".up.railway.app", "nishpa-production.up.railway.app", "nishpa-uat.up.railway.app", "authentic-commitment.up.railway.app", "*", "web-production-83c46.up.railway.app"]

CSRF_TRUSTED_ORIGINS = [
    "https://*.up.railway.app",
    "https://*.onrender.com",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inquiry',
    'inquiry_dashboard',
    'quotation',
    'proforma_invoice',
    'purchase_order',
    'grn',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nishpa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nishpa.wsgi.application'
ASGI_APPLICATION = 'nishpa.asgi.application'

# Prod
# os.environ["DATABASE_URL"] = "postgresql://postgres:vNgYaDJcapcKNifoLxLLmObtLyUucJhm@ballast.proxy.rlwy.net:27381/railway"

# UAT
# mindful-hope
os.environ["DATABASE_URL"] = "postgresql://postgres:bOCUOVqNqFCYXWGoAFCyIufUHTiXgHJZ@mainline.proxy.rlwy.net:32698/railway"

db_url = os.environ.get("DATABASE_URL")
# logging.info(f"DATABASE_URL: {db_url}")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

if db_url:
    DATABASES = {
        "default": dj_database_url.config(
            default=db_url,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
