import os
from pathlib import Path

# 1. НЕГИЗГИ ЖОЛДОР
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. КООПСУЗДУК ЖӨНДӨӨЛӨРҮ
SECRET_KEY = 'django-insecure-6!n5z08-ouw9u47_%k_01&^d^7=4_y4gxo(vcnqx8cl1v*c7ul'
DEBUG = True
ALLOWED_HOSTS = ['*']  # Иштеп жаткан учурда баарын ийкемдүү кылат

# 3. ТИРКЕМЕЛЕР (APPS)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сенин колдонмолоруң
    'config',
    'rest_framework',
    'rest_framework.authtoken',  # Токен менен иштөө үчүн
    'drf_spectacular',  # Swagger документтери үчүн
]

# 4. ОРТОНКУ КАТМАРЛАР (MIDDLEWARE)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'servic.urls'

# 5. ШАБЛОНДОР (TEMPLATES)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Эгер өзүнчө папкаң болсо
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

WSGI_APPLICATION = 'servic.wsgi.application'

# 6. БАЗА (DATABASE)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 7. КОЛДОНУУЧУНУН МОДЕЛИ
AUTH_USER_MODEL = 'config.User'

# 8. ПАРОЛЬ ВАЛИДАЦИЯСЫ
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# 9. ТИЛ ЖАНА УБАКЫТ
LANGUAGE_CODE = 'ky'  # Кыргыз тилине койсоң болот же 'en-us'
TIME_ZONE = 'Asia/Bishkek'
USE_I18N = True
USE_TZ = True

# 10. СТАТИКА ЖАНА МЕДИА (ФОТО/ВИДЕО)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 11. DJANGO REST FRAMEWORK ЖӨНДӨӨЛӨРҮ
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # Swagger схемасы
}

# 12. SWAGGER (DRF SPECTACULAR) ЖӨНДӨӨЛӨРҮ
SPECTACULAR_SETTINGS = {
    'TITLE': 'Service.kg API',
    'DESCRIPTION': 'Сервис порталынын API документтери (Swagger)',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,  # Токенди эстеп калат
        'displayOperationId': True,
    },
}

# 13. АВТОРИЗАЦИЯНЫ БАГЫТТОО
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

