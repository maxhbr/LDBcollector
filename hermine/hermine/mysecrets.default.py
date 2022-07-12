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


# For configuring OAuthn the following parameters are required :

# OAUTH_CLIENT = {
#     "client_id": "111111111111111",
#     "client_secret": "1111111111111111111111111111111",
#     "access_token_url": "https://github.com/login/oauth/authorize",
#     "authorize_url": "https://github.com/login/oauth/access_token",
#     "user_url": "https://api.github.com/user",  # provider URL for getting user data after token exchange
#     "user_details": lambda res: {               # generates username and email from user data
#         "username": res.get("login"),
#         "email": res.get("email"),
#     },
#    "id_key" : "uid", # the key for unique user id in user_url response (optional, "id" by default)
# }
