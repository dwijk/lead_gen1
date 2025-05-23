import os
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-93ee(@&&trw=muh6t&s=z$quwb!^6bi9p-$xhzgbm@#hy21bkq"

# SECURITY WARNING: don't run with debug turned on in production!



# DEBUG = True
DEBUG = False

ALLOWED_HOSTS = ["*"]
# ALLOWED_HOSTS = ['.vercel.app', '.now.sh','vercel.app']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "app",
    "django_cron",
    "background_task",
]

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "demo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = "demo.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases




DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}



# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': "lead_generation",
#         'USER': "agentai",
#         'PASSWORD': "Ai@agent#2024", 
#         'HOST': "165.22.217.108",
#         'PORT': "3306"}
# }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"

# Directory where you store static files to be collected (Optional)
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # Remove if you don't use custom static directories

# Directory where collected static files will be stored (for deployment)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build')  # Must match the distDir in vercel.json

# If using whitenoise to serve static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field



JAZZMIN_SETTINGS = {
    "site_title": "My Admin",
    "site_header": "My Dashboard",
    "site_brand": "My Brand",
    "welcome_sign": "Welcome to My Admin Panel",
    "copyright": "My Company",
    "search_model": ["auth.User", "app.UserData"],

    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "auth.User"},
        {"app": "yourapp"},
    ],

    "icons": {
        "auth": "fas fa-users-cog",
        "yourapp.YourModel": "fas fa-database",
    },
}


CRONJOBS = [
    ('*/1 * * * *', 'app.cron.MyCronJob')
]