# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

# This file has to be completed under the name 'mysecrets.py' in this same folder.
# Do not delete or modify this file, it's used for documentation build in CI !
# Do not commit your authentication credential !

SECRET_KEY = "your-django-secret-key"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "db.sqlite3"}}

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


# # For local development : external definition of var env
# # Load environment definition file
# ENV_FILE = find_dotenv()
# if ENV_FILE:
#     load_dotenv(ENV_FILE)
#
# # Load OAUTH application settings into memory
# OAUTH_DOMAIN = os.environ.get("OAUTH_DOMAIN")
# OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID")
# OAUTH_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET")
# OAUTH_SCOPE = os.environ.get("OAUTH_SCOPE")   # list of scope separated by ','
# OAUTH_ID_KEY = os.environ.get("OAUTH_ID_KEY")
#
# # For configuring OAuthn the following parameters are required :
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
