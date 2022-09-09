import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_NAME"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": "db",
        "PORT": 5432,
    }
}

SECRET_KEY = os.environ.get("SECRET")

# # Load Auth0 application settings into memory
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")
AUTH0_SCOPE = os.environ.get("AUTH0_SCOPE")         # list of scope separated by ','
AUTH0_ID_KEY = os.environ.get("AUTH0_ID_KEY")

# For configuring OAuthn the following parameters are required :
if AUTH0_DOMAIN is not None:
    OAUTH_CLIENT = {
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "access_token_method": "POST",
        "access_token_url": "https://{domain}/oauth/token".format(domain=AUTH0_DOMAIN),
        "authorize_url": "https://{domain}/authorize".format(domain=AUTH0_DOMAIN),
        "scope": AUTH0_SCOPE.split(","), # must be a array of scope, example ['openid', 'profile', 'email']
        "user_url": "https://{domain}/userinfo".format(domain=AUTH0_DOMAIN), # provider URL for getting user data after token exchange
        "id_key": AUTH0_ID_KEY,  # unique id of userinfo, example : sub
        "user_details": lambda res: {  # generates username and email from user data
            "username": res.get("nickname"),
            "email": res.get("email"),
        },
    }
