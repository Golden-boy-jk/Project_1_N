import os
from pathlib import Path

import environ
from celery.schedules import crontab

# --- Base paths / env ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(
    DEBUG=(bool, False),
    TIME_ZONE=(str, "Europe/Moscow"),
    LANGUAGE_CODE=(str, "ru"),
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# --- Core ---------------------------------------------------------------------
DEBUG = env("DEBUG", default=False)
SECRET_KEY = env("SECRET_KEY", default="insecure-secret-key")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

# --- Database -----------------------------------------------------------------
DATABASES = {"default": env.db(default=f"sqlite:///{BASE_DIR}/db.sqlite3")}

# --- Installed apps -----------------------------------------------------------
INSTALLED_APPS = [
    # i18n for models
    "modeltranslation",
    # django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.flatpages",
    # project apps
    "accounts",
    "news.apps.NewsConfig",
    # auth / social
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.yandex",
    # API
    "rest_framework",
]

SITE_ID = 1

# --- Middleware ---------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# --- URLs / WSGI --------------------------------------------------------------
ROOT_URLCONF = "NewsPortal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "NewsPortal.wsgi.application"

# --- Auth password validators -------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n / l10n --------------------------------------------------------------
MODELTRANSLATION_DEFAULT_LANGUAGE = "ru"
LANGUAGES = [
    ("ru", "Russian"),
    ("en", "English"),
]
LANGUAGE_CODE = env("LANGUAGE_CODE", default="ru")
TIME_ZONE = env("TIME_ZONE", default="Europe/Moscow")
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

# --- Static / Media -----------------------------------------------------------
STATIC_URL = "/static/"
# STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # enable on prod

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Django Allauth -----------------------------------------------------------
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/accounts/profile/"
LOGOUT_REDIRECT_URL = "/news/"

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SIGNUP_FIELDS = ["email", "password1", "password2"]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SOCIALACCOUNT_PROVIDERS = {
    "yandex": {
        "APP": {
            "client_id": "",
            "secret": "",
        },
        "SCOPE": ["login:email"],
        "AUTH_PARAMS": {"force_confirm": "yes"},
    }
}

# --- Email --------------------------------------------------------------------
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@example.com")
SERVER_EMAIL = EMAIL_HOST_USER
SITE_URL = "http://127.0.0.1:8000"

ADMINS = [("Admin", "admin@example.com")]

# --- Celery / Beat ------------------------------------------------------------
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CELERY_BEAT_SCHEDULE = {
    "send_weekly_newsletter": {
        "task": "news.tasks.send_weekly_newsletter",
        "schedule": crontab(hour=8, minute=0, day_of_week=1),  # Mon 08:00
    },
}

# --- Cache --------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(BASE_DIR, "cache_files"),
        "TIMEOUT": 300,
    }
}
