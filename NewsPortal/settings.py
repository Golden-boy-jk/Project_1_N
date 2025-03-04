import os.path
from pathlib import Path
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-2za(ynv-&og)n8!%vk2e=u3=5-(k!6f*ip%0i%=m_1@2k37$4#'


DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'accounts',
    'django_apscheduler',
    'news.apps.NewsConfig',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.yandex',
    'django_celery_beat',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
APSCHEDULER_RUN_NOW_TIMEOUT = 25

SCHEDULER_JOBSTORES = {
    'default': {
        'type': 'django_apscheduler.jobstores.DjangoJobStore',
    }
}
SCHEDULER_EXECUTORS = {
    'default': {
        'type': 'threadpool',
        'max_workers': 20,
    }
}
SCHEDULER_JOB_DEFAULTS = {
    'coalesce': False,
    'max_instances': 3,
}
SCHEDULER_TIMEZONE = 'UTC'

ROOT_URLCONF = 'NewsPortal.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'NewsPortal.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

SOCIALACCOUNT_PROVIDERS = {
    'yandex': {
        'APP': {
            'client_id': '3c52fc6f82884e82b4ad633b2c027a58',
            'secret': 'a912c0c5d6204bd8b28d21af34453e7d',
        },
        'SCOPE': ['login:email'],
        'AUTH_PARAMS': {'force_confirm': 'yes'},
    }
}


STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/profile/'
LOGOUT_REDIRECT_URL = '/news/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_SIGNUP_REDIRECT_URL = '/'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_LOGIN_METHODS = ['email']
# ACCOUNT_FORMS = {'signup': 'sign.models.BasicSignupForm'}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'почта'
EMAIL_HOST_PASSWORD = 'пароль от приложения'  # пароль от почты
DEFAULT_FROM_EMAIL = 'почта'
SERVER_EMAIL = EMAIL_HOST_USER
SITE_URL = 'http://127.0.0.1:8000'
ABSOLUTE_URL_OVERRIDES = {
    'news.post': lambda o: f"/posts/{o.id}/"
}
ADMINS = [('Admin', 'game.kuzin@gmail.com'),]
# MANAGERS = [('Manager', 'почто менеджера')]

CELERY_BROKER_URL = 'redis://:ваш пароль-11985.c135.eu-central-1-1.ec2.redns.redis-cloud.com:11985'
CELERY_RESULT_BACKEND = 'redis://:ваш пароль-11985.c135.eu-central-1-1.ec2.redns.redis-cloud.com:11985'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10
CELERY_BROKER_CONNECTION_TIMEOUT = 30


CELERY_BEAT_SCHEDULE = {
    'send_weekly_newsletter': {
        'task': 'news.tasks.send_weekly_newsletter',  # Путь к вашей задаче
        'schedule': crontab(hour=8, minute=0, day_of_week=1),  # Понедельник, 8:00 утра
    },
}

