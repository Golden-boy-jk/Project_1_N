import os
from pathlib import Path
from celery.schedules import crontab
from dotenv import load_dotenv  

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv(
    "SECRET_KEY", "django-insecure-2za(ynv-&og)n8!%vk2e=u3=5-(k!6f*ip%0i%=m_1@2k37$4#"
)

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


INSTALLED_APPS = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.flatpages",
    "accounts",
    "django_apscheduler",
    "news.apps.NewsConfig",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.yandex",
    "rest_framework",
]

SITE_ID = 1

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
    "allauth.account.middleware.AccountMiddleware", # Рекомендованное положение - после SessionMiddleware
]


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


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


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


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
LANGUAGE_CODE = "ru"
MODELTRANSLATION_DEFAULT_LANGUAGE = "ru"
LANGUAGES = [
    ("ru", "Russian"),
    ("en", "English"),
]
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"), # Убран лишний 'NewsPortal'
]

TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = "/static/"
# STATIC_ROOT = os.path.join(BASE_DIR, 'static') # Раскомментируйте для продакшена

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Allauth settings
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/accounts/profile/"
LOGOUT_REDIRECT_URL = "/news/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_SIGNUP_REDIRECT_URL = "/"

ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']

# ALLAUTH — современный синтаксис
ACCOUNT_LOGIN_METHODS = {"email"}    
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*'] 
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = 'optional'  
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]




SOCIALACCOUNT_PROVIDERS = {
    "yandex": {
        "APP": {
            "client_id": os.getenv("YANDEX_CLIENT_ID"),
            "secret": os.getenv("YANDEX_SECRET"),
        },
        "SCOPE": ["login:email"],
        "AUTH_PARAMS": {"force_confirm": "yes"},
    }
}


# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.yandex.ru"
EMAIL_PORT = 587
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
SERVER_EMAIL = EMAIL_HOST_USER
SITE_URL = "http://127.0.0.1:8000"

ADMINS = [
    ("Admin", os.getenv("ADMIN_EMAIL")),
]

# Celery settings
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CELERY_BEAT_SCHEDULE = {
    "send_weekly_newsletter": {
        "task": "news.tasks.send_weekly_newsletter",
        "schedule": crontab(hour=8, minute=0, day_of_week=1),  # Понедельник, 8:00
    },
}

# Caching
CACHES = {
    "default": {
        "TIMEOUT": 300,
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(BASE_DIR, "cache_files"),
    }
}


# Django-apscheduler settings
# ИСПРАВЛЕНО: Названия настроек обновлены
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
APSCHEDULER_RUN_NOW_TIMEOUT = 25
APSCHEDULER_JOBSTORES = {
    "default": {
        "type": "django_apscheduler.jobstores.DjangoJobStore",
    }
}
APSCHEDULER_EXECUTORS = {
    "default": {
        "type": "threadpool",
        "max_workers": 20,
    }
}
APSCHEDULER_JOB_DEFAULTS = {
    "coalesce": False,
    "max_instances": 3,
}
APSCHEDULER_TIMEZONE = TIME_ZONE # Использование TIME_ZONE проекта
