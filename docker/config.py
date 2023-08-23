import os

DEBUG = os.environ.get("PRODUCTION").lower() == "false"
ENABLE_PROFILING = os.environ.get("ENABLE_PROFILING").lower() == "true"
HOST = os.environ.get("HOST")
STATIC_ROOT = os.environ.get("STATIC_ROOT")

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
    }
