import os

DEBUG = os.environ.get("PRODUCTION", "").lower() == "false"
ENABLE_PROFILING = os.environ.get("ENABLE_PROFILING", "").lower() == "true"
HOST = os.environ.get("HOST")

FORCE_SCRIPT_NAME = os.environ.get("FORCE_SCRIPT_NAME")
STATIC_ROOT = "/opt/hermine/static"
MAX_UPLOAD_SIZE = (
    int(os.environ.get("MAX_UPLOAD_SIZE"))
    if os.environ.get("MAX_UPLOAD_SIZE")
    else 10485760
)
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS")

if os.environ.get("TRUST_PROXY_HEADERS", "").lower() == "true":
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_NAME"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
    }
}

SECRET_KEY = os.environ.get("SECRET")
AUTH_TOKEN_HASH = os.environ.get("AUTH_TOKEN_HASH") or "sha256"

# SMTP settings
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "").lower() == "true"
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "").lower() == "true"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")

AZUREAD_TENANT_ID = os.environ.get("AZUREAD_TENANT_ID")

# Load OAuth application settings into memory
OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID")
OAUTH_DOMAIN = os.environ.get("OAUTH_DOMAIN")
OAUTH_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET")
OAUTH_SCOPE = os.environ.get("OAUTH_SCOPE")  # list of scope separated by ','
OAUTH_ID_KEY = os.environ.get("OAUTH_ID_KEY")
OAUTH_TOKEN_URL = os.environ.get("OAUTH_TOKEN_URL")
OAUTH_AUTHORIZE_URL = os.environ.get("OAUTH_AUTHORIZE_URL")
OAUTH_USER_URL = os.environ.get("OAUTH_USER_URL")
OAUTH_USERNAME_PROPERTY = os.environ.get("OAUTH_USERNAME_PROPERTY", "username")
SOCIAL_AUTH_REDIRECT_IS_HTTPS = os.environ.get("SOCIAL_AUTH_REDIRECT_IS_HTTPS")

KEYCLOAK_DOMAIN = os.environ.get("KEYCLOAK_DOMAIN")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.environ.get("KEYCLOAK_CLIENT_SECRET")
KEYCLOAK_ID_KEY = os.environ.get("KEYCLOAK_ID_KEY")
KEYCLOAK_TOKEN_URL = os.environ.get("KEYCLOAK_TOKEN_URL")
KEYCLOAK_AUTHORIZE_URL = os.environ.get("KEYCLOAK_AUTHORIZE_URL")

if AZUREAD_TENANT_ID is not None:
    AZUREAD_CLIENT = {
        "client_id": OAUTH_CLIENT_ID,
        "client_secret": OAUTH_CLIENT_SECRET,
        "tenant_id": AZUREAD_TENANT_ID,
        "host": f"https://{HOST}",  # host for redirect_uri
    }

# For configuring OAuth the following parameters are required :
if OAUTH_CLIENT_ID is not None:
    OAUTH_CLIENT = {
        "client_id": OAUTH_CLIENT_ID,
        "client_secret": OAUTH_CLIENT_SECRET,
        "access_token_method": "POST",
        "access_token_url": OAUTH_TOKEN_URL,
        "authorize_url": OAUTH_AUTHORIZE_URL,
        "scope": OAUTH_SCOPE.split(
            ","
        ),  # must be a array of scope, example ['openid', 'profile', 'email']
        "user_url": OAUTH_USER_URL,  # provider URL for getting user data after token exchange
        "id_key": OAUTH_ID_KEY,  # unique id of userinfo, example : sub, or id
        "user_details": lambda res: {  # generates username and email from user data
            "username": res.get(OAUTH_USERNAME_PROPERTY),
            "email": res.get("email"),
        },
        "host": f"https://{HOST}",  # host for redirect_uri
    }
# For configuring KEYCLOAK the following parameters are required :
if KEYCLOAK_CLIENT_ID is not None:
    KEYCLOAK_CLIENT = {
        "domain": KEYCLOAK_DOMAIN,
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "access_token_url": KEYCLOAK_TOKEN_URL,
        "authorize_url": KEYCLOAK_AUTHORIZE_URL,
        "id_key": KEYCLOAK_ID_KEY,
    }
