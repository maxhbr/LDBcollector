# SPDX-FileCopyrightText: 2023 Inno3
# SPDX-License-Identifier: AGPL-3.0-only

# This file has to be completed under the name 'config.py' in this same folder.
# Do not delete or modify this file, it's used for documentation build in CI !
# Do not commit your authentication credential !

# use os.environ.get("VAR_NAME") if you prefer to take config from environment variables
# (the config.py inside docker/ is a good example of this)

import os

from django.conf import settings

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "your-django-secret-key"

HOST = "example.com"
# CSRF_TRUSTED_ORIGINS = ["https://" + HOST] # only required if you use a reverse proxy

# Static files location, defaults to static/ in the Hermine root dir
# In production, static files should be served by a web server like nginx
# STATIC_ROOT = "/path/to/static/root"

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(settings.BASE_DIR, "db.sqlite3"),
    }
}

# For a Postgres DB, copy and fill the following :

# DATABASES  = {
#     'default':{
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": "your-postgres-db-name",
#         "USER": "your-postgres-db-user",
#         "PASSWORD": "your-postgres-db-password",
#         "HOST": "",
#         "PORT": ""
#     }
# }

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB, you have to set it in bytes

# # For configuring OAuthn the following parameters are required :
# OAUTH_DOMAIN =
# OAUTH_CLIENT_ID =
# OAUTH_CLIENT_SECRET =
# OAUTH_SCOPE =
# OAUTH_ID_KEY =
# OAUTH_CLIENT = {
#     "client_id": OAUTH_CLIENT_ID,
#     "client_secret": OAUTH_CLIENT_SECRET,
#     "scope": OAUTH_SCOPE.split(","),  # must be a array of scope
#     "access_token_method": "POST",
#     "access_token_url": "https://{domain}/oauth/token".format(domain=OAUTH_DOMAIN),
#     "authorize_url": "https://{domain}/authorize".format(domain=OAUTH_DOMAIN),
#     "user_url": "https://{domain}/userinfo".format(domain=OAUTH_DOMAIN), # provider URL for getting user data after token exchange
#     "id_key": OAUTH_ID_KEY,  # unique id of userinfo, example : sub
#     "user_details": lambda res: {  # generates username and email from user data
#         "username": res.get("nickname"),
#         "email": res.get("email"),
#     },
# }

# Path to the current version to be displayed in the footer
# VERSION_FILE_PATH = "hermine/hermine/VERSION.txt"

# SECURITY WARNING: don't run with debug or profiling turned on in production!
# DEBUG = True
# ENABLE_PROFILING = True
