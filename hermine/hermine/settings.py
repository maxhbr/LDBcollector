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
import re

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

if hasattr(config, "ALLOWED_HOSTS"):
    ALLOWED_HOSTS = config.ALLOWED_HOSTS
elif hasattr(config, "HOST"):
    ALLOWED_HOSTS = [config.HOST]
else:
    ALLOWED_HOSTS = []

if csrf := getattr(config, "CSRF_TRUSTED_ORIGINS", None):
    if isinstance(csrf, list):
        # well formatted list of https://example.com as in config.default.py
        CSRF_TRUSTED_ORIGINS = csrf
    elif isinstance(csrf, str):
        # single string (from environment) as in docker config.py
        CSRF_TRUSTED_ORIGINS = [
            origin if re.match("^https?://", origin) else "https://" + origin
            for origin in csrf.split(",")
        ]
elif host := getattr(config, "HOST", None):
    CSRF_TRUSTED_ORIGINS = ["https://" + host]

if getattr(config, "FORCE_SCRIPT_NAME", None):
    FORCE_SCRIPT_NAME = config.FORCE_SCRIPT_NAME

USE_X_FORWARDED_HOST = getattr(config, "USE_X_FORWARDED_HOST", False)
SECURE_PROXY_SSL_HEADER = getattr(config, "SECURE_PROXY_SSL_HEADER", None)

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.forms",
    "social_django",
    "rest_framework",
    "django_filters",
    "hermine",
    "cube.apps.CubeConfig",
    "drf_yasg",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if getattr(config, "REMOTE_USER_HEADER", None):
    MIDDLEWARE.append("cube.middlewares.RemoteUserMiddleware")
    REMOTE_USER_HEADER = config.REMOTE_USER_HEADER

ROOT_URLCONF = "hermine.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
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

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

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
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
SOCIAL_AUTH_URL_NAMESPACE = "social"

if getattr(config, "OAUTH_CLIENT", None) is not None:
    OAUTH_CLIENT = config.OAUTH_CLIENT
    SOCIAL_AUTH_DEFAULT_KEY = OAUTH_CLIENT["client_id"]
    SOCIAL_AUTH_DEFAULT_SECRET = OAUTH_CLIENT["client_secret"]
    SOCIAL_AUTH_DEFAULT_HOST = OAUTH_CLIENT["host"]
    AUTHENTICATION_BACKENDS.append("cube.oauth.OAuth2")


if getattr(config, "AZUREAD_CLIENT", None) is not None:
    AZUREAD_CLIENT = config.AZUREAD_CLIENT
    SOCIAL_AUTH_AZUREAD_KEY = AZUREAD_CLIENT["client_id"]
    SOCIAL_AUTH_AZUREAD_SECRET = AZUREAD_CLIENT["client_secret"]
    SOCIAL_AUTH_AZUREAD_TENANT_ID = AZUREAD_CLIENT["tenant_id"]
    SOCIAL_AUTH_AZUREAD_HOST = AZUREAD_CLIENT["host"]
    AUTHENTICATION_BACKENDS.append("cube.azuread_auth.Entra")

# keycloak
if getattr(config, "KEYCLOAK_CLIENT", None) is not None:
    KEYCLOAK_CLIENT = config.KEYCLOAK_CLIENT
    SOCIAL_AUTH_KEYCLOAK_BASE_URL = KEYCLOAK_CLIENT["domain"]
    SOCIAL_AUTH_KEYCLOAK_KEY = KEYCLOAK_CLIENT["client_id"]
    SOCIAL_AUTH_KEYCLOAK_SECRET = KEYCLOAK_CLIENT["client_secret"]
    SOCIAL_AUTH_KEYCLOAK_PUBLIC_KEY = KEYCLOAK_CLIENT["id_key"]
    SOCIAL_AUTH_KEYCLOAK_AUTHORIZATION_URL = KEYCLOAK_CLIENT["authorize_url"]
    SOCIAL_AUTH_KEYCLOAK_ACCESS_TOKEN_URL = KEYCLOAK_CLIENT["access_token_url"]
    SOCIAL_AUTH_KEYCLOAK_ID_KEY = "email"
    AUTHENTICATION_BACKENDS.append("cube.keycloak_auth.KeycloakBackend")


# SMTP

if getattr(config, "EMAIL_HOST", None) is not None:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
if getattr(config, "EMAIL_HOST", None) is not None:
    EMAIL_HOST = config.EMAIL_HOST
if getattr(config, "EMAIL_PORT", None) is not None:
    EMAIL_PORT = config.EMAIL_PORT
if getattr(config, "EMAIL_HOST_USER", None) is not None:
    EMAIL_HOST_USER = config.EMAIL_HOST_USER
if getattr(config, "EMAIL_HOST_PASSWORD", None) is not None:
    EMAIL_HOST_PASSWORD = config.EMAIL_HOST_PASSWORD
if getattr(config, "DEFAULT_FROM_EMAIL", None) is not None:
    DEFAULT_FROM_EMAIL = config.DEFAULT_FROM_EMAIL
if getattr(config, "EMAIL_USE_TLS", None) is not None:
    EMAIL_USE_TLS = config.EMAIL_USE_TLS
if getattr(config, "EMAIL_USE_SSL", None) is not None:
    EMAIL_USE_SSL = config.EMAIL_USE_SSL


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "static/"
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

STATICFILES_DIRS = [
    os.path.join(os.path.dirname(BASE_DIR), "hermine/vite_modules", "dist"),
    os.path.join(os.path.dirname(BASE_DIR), "hermine/vite_modules", "src", "hermine"),
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    }
}

LOGIN_REDIRECT_URL = "cube:dashboard"
LOGIN_URL = "login"

# Always send errors to console
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO" if DEBUG else "ERROR",
            "propagate": False,
        }
    },
}

# Added After migration to Django 3.2
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# REST API stuff
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions
    "DEFAULT_PERMISSION_CLASSES": ["cube.permissions.ReadWriteDjangoModelPermissions"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "cube.auth.HashedTokenAuthentication",
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
try:
    with open(os.path.join(BASE_DIR, "..", "pyproject.toml")) as f:
        for line in f:
            if line.startswith("version"):
                VERSION = line.split("=")[1].strip().strip('"')
except FileNotFoundError:
    VERSION = "Unknown"

# Silk config

ENABLE_PROFILING = getattr(config, "ENABLE_PROFILING", False)
if ENABLE_PROFILING:
    INSTALLED_APPS.append("silk")
    MIDDLEWARE.insert(1, "silk.middleware.SilkyMiddleware")
    SILKY_PYTHON_PROFILER = True
    SILKY_AUTHENTICATION = True
    SILKY_AUTHORISATION = True

    def SILKY_INTERCEPT_FUNC(request):
        return not request.path.startswith("/static/")

    def SILKY_PERMISSIONS(user):
        return user.is_superuser


MAX_UPLOAD_SIZE = getattr(config, "MAX_UPLOAD_SIZE", 10 * 1024 * 1024)
