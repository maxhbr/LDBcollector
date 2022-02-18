# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: AGPL-3.0-only

# This file has to be completed under the name 'mysecrets.py' in this same folder.
# Do not delete or modify this file, it's used for documentation build in CI !
# Do not commit your authentication credential !

# DATABASES = {
#     "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "db.sqlite3"}
# }

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
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "hermine",
        "USER": "hermine",
        "PASSWORD": "hermine",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

SECRET_KEY = "your-django-secret-key"
