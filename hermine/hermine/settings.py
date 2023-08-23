# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Django settings for hermine project.

You are not supposed to edit this file : it is
part of Hermine source code and contains settings which
should be the same for all Hermine installations.

To edit your specific install config create a file named config.py
"""

import os

from django.contrib import messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import hermine.config as config  # noqa E402
except ImportError:
    # Fallback to legacy name
    try:
        import hermine.mysecrets as config  # noqa E402
    except ImportError:
        raise ImportError(
            "No config file found. Please create a config.py file in the hermine folder."
        )

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getattr(config, "DEBUG", False)

if (host := getattr(config, "HOST", None)) is not None:
    ALLOWED_HOSTS = [host]
    if (csrf := getattr(config, "CSRF_TRUSTED_ORIGINS", None)) is not None:
        host = csrf
    CSRF_TRUSTED_ORIGINS = ["https://" + host]
    USE_X_FORWARDED_HOST = True
else:
    ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "cube.apps.CubeConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "social_django",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "hermine",
    "drf_yasg",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hermine.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            # Empty before build
            os.path.join(os.path.dirname(BASE_DIR), "hermine/vite_modules", "dist"),
            os.path.join(os.path.dirname(BASE_DIR), "hermine/vite_modules", "src"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "social_django.context_processors.backends",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cube.utils.reference.shared_reference_loaded_context_processor",
            ]
        },
    }
]

MESSAGE_TAGS = {
    messages.INFO: "primary",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}


WSGI_APPLICATION = "hermine.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = config.DATABASES
DATABASES["shared"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.path.join(BASE_DIR, "shared.sqlite3"),
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa E501
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# OAuth support

if getattr(config, "OAUTH_CLIENT", None) is not None:
    OAUTH_CLIENT = config.OAUTH_CLIENT
    SOCIAL_AUTH_DEFAULT_KEY = OAUTH_CLIENT["client_id"]
    SOCIAL_AUTH_DEFAULT_SECRET = OAUTH_CLIENT["client_secret"]
    AUTHENTICATION_BACKENDS = [
        "cube.oauth.OAuth2",
        "django.contrib.auth.backends.ModelBackend",
    ]
    SOCIAL_AUTH_URL_NAMESPACE = "social"


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = getattr(config, "STATIC_ROOT", os.path.join(BASE_DIR, "..", "static"))

APPEND_SLASH = True

FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]

STATICFILES_FINDERS = [
    # First add the two default Finders, since this will overwrite the default.
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# The following line raises a Warning. Moving the folder to the right place does not
# fix it.
STATICFILES_DIRS = [
    os.path.join(os.path.dirname(BASE_DIR), "hermine/vite_modules", "dist", "hermine"),
    os.path.join(os.path.dirname(BASE_DIR), "hermine/vite_modules", "src", "hermine"),
]
LOGIN_REDIRECT_URL = "/"

# Added After migration to Django 3.2
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# REST API stuff
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

ENTERPRISE_NAME = "inno3"
GITLAB_TOKEN = ""
COMMUNITY_GITLAB = "https://gitlab.com/hermine-project/community-data.git"

DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000000

# Graph vizualization stuff

GRAPH_MODELS = {"all_applications": True, "group_models": True}

# Version
with open(os.path.join(BASE_DIR, "..", "pyproject.toml")) as f:
    for line in f:
        if line.startswith("version"):
            VERSION = line.split("=")[1].strip().strip('"')

# Silk config

ENABLE_PROFILING = getattr(config, "ENABLE_PROFILING", False)
if ENABLE_PROFILING:
    INSTALLED_APPS.append("silk")
    MIDDLEWARE.insert(1, "silk.middleware.SilkyMiddleware")
    SILKY_PYTHON_PROFILER = True
    SILKY_AUTHENTICATION = True
    SILKY_AUTHORISATION = True

    def SILKY_PERMISSIONS(user):
        return user.is_superuser
