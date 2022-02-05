from celery.schedules import crontab
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")
VERIFYCODE_KEY = config("VERIFYCODE_KEY")
VERIFYCODETOKEN_KEY = config("VERIFYCODETOKEN_KEY")
DEVICETOKEN_KEY = config("DEVICETOKEN_KEY")
ACCESSTOKEN_KEY = config('ACCESSTOKEN_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1"
]

AUTH_USER_MODEL = 'user.User'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',

    'rest_framework',
    'rest_framework_nested',
    'drf_spectacular',
    'debug_toolbar',

    'conversation',
    'community',
    'user',
    'core',
    'auth_app',
    'picturic',
    'global_id',
]


CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:8000',
)

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'auth_app.authentication.AccessTokenAuthentication',
    ],
    'DEFAULT_THROTTLE_RATES': {
        # second, minute, hour, day
        'anon': '40/minute',
        'user': '50/minute',
    },
    'DEFAULT_SCHEMA_CLASS': "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Messenger API',

    'CONTACT': {
        'name': 'Matin Khaleghi',
        'url': "https://t.me/ThePokerFaCe",
        'email': "matin.khaleghi.nezhad@gmail.com"
    },
    'LICENSE': {'name': "MIT"},
    'VERSION': '1.0.0',
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
}

INTERNAL_IPS = [  # It's for debug tool
    '127.0.0.1',
]

GLOBAL_ID_CHAT_SERIALIZERS = {
    'user.models.User': 'user.serializers.UserSerializer',
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'messenger.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'messenger.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'messenger',
    #     'HOST': config("DB_HOST"),
    #     'USER': config("DB_USER"),
    #     'PASSWORD': config("DB_PASSWORD"),
    # }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = BASE_DIR / 'static'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Celery settings
# https://docs.celeryproject.org/en/stable/userguide/configuration.html#example-configuration-file

BROKER_URL = config('BROKER_URL')
CELERY_RESULT_BACKEND = config('RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERYBEAT_SCHEDULE = {
    'delete_inactive_users': {
        'task': 'user.tasks.delete_inactive_users',
        'schedule': crontab(minute=0, hour='*/1')
    }
}
