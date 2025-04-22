<!---
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr>
SPDX-License-Identifier: CC-BY-4.0
-->

# Installing Hermine for production


## Getting the code

You can download latest releases from [Hermine releases page](https://gitlab.com/hermine-project/hermine/-/releases)
or clone latest development version from [GitLab](https://gitlab.com/hermine-project/hermine/-/tree/main):

```bash
git clone https://gitlab.com/hermine-project/hermine.git
cd hermine/
```

Major versions changes mean breaking changes, either in the installation configuration or in the API.
You can find more information in [CHANGELOG.md](https://gitlab.com/hermine-project/hermine/-/blob/main/CHANGELOG.md).

For minor or patch versions, it should be safe to update your instance by pulling the latest tag from the repository or
downloading from the release page.


## Docker Compose

Hermine provides a [Docker Compose](https://docs.docker.com/compose/) configuration with the
following services:
* a PostgreSQL database version 16
* a [gunicorn](https://gunicorn.org/) server for the Python backend
* an optional [Caddy](https://caddyserver.com/) server to deploy Hermine with HTTPS out-of-the-box

Beware this config is for `docker compose`
([Compose v2](https://docs.docker.com/compose/migrate/))
not for `docker-compose` (Compose v1).

Two profiles are available :
* a default profile to use Hermine on a local machine or behind a reverse proxy (not suited for development)
* an `https` profile where Caddy is configured with automatic HTTPS. It can easily be
deployed on a VPS.

Configuration is made through a [`.env` file](https://github.com/bkeepers/dotenv) which should be
placed at the root of the project. Relevant [configuration variables
for Hermine image](#image-configuration) are exposed through Compose with
the prefix `HERMINE_`. Check [docker-compose.yml](https://gitlab.com/hermine-project/hermine/-/blob/main/docker-compose.yml)
comments for more information.

At first launch, a superadmin user is created with `admin / admin` credential.
You can update these credentials from `http://example.com/admin/auth/user/`.

In case you need to access the `django-admin` tool from outside Docker, you should use :
`docker exec -it hermine_django_1 /opt/hermine/manage.py`

To automatically init the database with [reference data](reference_data.md), just put the `shared.json` file in the `docker/` directory
before starting the containers.

### Default profile (to use locally or behind a reverse proxy)

You must set `PORT` instead of `HERMINE_HOST` variable.

```bash
# configure secret key
echo "HERMINE_SECRET=RANDOMSTRINGFORSECURITY" > .env
# configure port
echo "PORT=9000" >> .env
# optional : configure HOST if you plan to use Hermine behind a reverse proxy
echo "HERMINE_HOST=example.com" >> .env
# start the services in background
docker compose up -d

# Visit http://localhost:9000 and login with admin / admin
```

### HTTPS profile (for deployment on a VPS)

You just need to set `HERMINE_SECRET` and `HERMINE_HOST` environment variables before
you can start the containers. The easiest way to do so is to
write it in a .env file.

```bash
# configure secret key
echo "HERMINE_SECRET=RANDOMSTRINGFORSECURITY" > .env
# optional : configure HOST if you use something else than localhost:80
echo "HERMINE_HOST=example.com" >> .env
# start the services in background
docker compose --profile https up -d
```

Hermine should be accessible at `https://example.com`. Caddy automatically sets up
and renew HTTPS certificates.

To update your instance :

```bash
git switch main && git pull
docker compose --profile https up -d --build
```

## Hermine Docker image

You can also use the Hermine Docker image to run Hermine in your own Docker environment,
without using Docker Compose. You will need to set up your own PostgreSQL database (version 14 required, 16 or above is recommended), as well as a reverse proxy to
serve static files and proxy other requests to the Docker image.

You first need to build the image :

```bash
docker build -t hermine .
```

### Image configuration

Runtime configuration is made through environment variables.
You can use a `.env` file to set them up.

The minimal configuration is :
* **SECRET**: the secret key used by Django to sign session cookies
* **DJANGO_PORT**: the port on which the container will listen for requests
* **POSTGRES_HOST**: the hostname of the PostgreSQL database
* **POSTGRES_PORT**: the port of the PostgreSQL database
* **POSTGRES_NAME**: the name of the PostgreSQL database
* **POSTGRES_USER**: the username to connect to the PostgreSQL database
* **POSTGRES_PASSWORD**: the password to connect to the PostgreSQL database
* **SUPERUSER**: the username of the superuser created at first launch
* **PASSWORD**: the password of the superuser created at first launch
* **HOST**: the external URL of your Hermine instance (ex: `example.com`), should be the same as the one used in the reverse proxy configuration
* **TRUST_PROXY_HEADERS**: should be set to "True" as you are using a reverse proxy
* **STATIC_ROOT**: the directory of the volume where static files will be stored

Optional configuration :
* **CSRF_TRUSTED_ORIGINS**: a list of trusted origins for CSRF protection, defaults to `[HOST]`
* **THREADS**: the number of threads used by gunicorn workers, defaults to number of CPU cores
* **MAX_UPLOAD_SIZE**: the maximum size that the SBOM to import can be (in bytes), defaults to 10MB

Other configuration variables are available, you can find them in the
[docker-compose.yml](https://gitlab.com/hermine-project/hermine/-/blob/main/docker-compose.yml) file.

Example of command to run the container :
```bash
docker run -d \
  --name hermine \
  --env-file .env \
  hermine
```

#### Postgres Tips
It's best practice to use a dedicated schema for each application and for specific users.

If you do this, you'll need to change the default schema for the user configured in `POSTGRES_USER` (e.g. myUser) to be able to use your dedicated schema (e.g. mySchema).
Otherwise, you may have problems, as your user shouldn't have the right to create tables in the `public` schema.
```sql
ALTER ROLE myUser SET search_path TO mySchema;
```

## Manual install

### Install python dependencies

You should run Hermine in a Python virtual environment.
Using [poetry](https://python-poetry.org/docs/), you can create the
virtual environment and install the dependencies with:

```bash
poetry install
```

### Install and build front modules

```bash
npm install
npm run build
```


```bash
poetry run hermine/manage.py collectstatic
```

### Configure your instance

Before the first run, you have to create a `config.py` file in the `hermine/hermine/` directory.

```
cp hermine/hermine/config.default.py hermine/hermine/config.py
```
Update `hermine/hermine/config.py` according to your configuration.
Ex: For development purposes, you can set `HOST` to `127.0.0.1` and `DEBUG` to `True`

Here are the parameters you may want to change in your `hermine/hermine/config.py` file

| Parameter name | Description | Default value |
| -------------- | ----- | ------------- |
| HOST |  The URL of your Hermine instance | "<span>example.com</span>" |
| MAX_UPLOAD_SIZE | The maximum size that the SBOM to import can be (in bytes) |10\*1024\*1024|
| SECRET_KEY | The key that Django will use to encrypt data | "your-django-secret-key" |
| DEBUG | Enables debug functionality, should be disabled in production | False |


Update the database structure and create a superuser :
```
# create database structure
poetry run hermine/manage.py migrate

# create a superuser
poetry run hermine/manage.py createsuperuser
```


### Run the server

How you want to serve Hermine is up to you. You should be familiar with WSGI servers and reverse proxies. You can find more information in
[Django documentation](https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/gunicorn/).

A typical installation is :

* Gunicorn or another WSGI server (running Hermine's `wsgi.py`)
* Nginx to proxy requests to Gunicorn and handle HTTPS

Static files are handled by [Whitenoise](https://whitenoise.readthedocs.io/), so
you can serve them directly from your WSGI server. Otherwise, Hermine is not different
from any other Django application. You can find more information in [Django documentation](https://docs.djangoproject.com/en/4.1/howto/deployment/).

For development purpose, you can simply run :

```bash
# run the server
poetry run hermine/manage.py runserver
```

## OAuth

You can use an OAuth2 server as authentication backend by setting OAuth parameters.

For Docker installs, the following environment variables can be set :
* **OAUTH_CLIENT_ID**
* **OAUTH_DOMAIN**
* **OAUTH_CLIENT_SECRET**
* **OAUTH_SCOPE**: list of scope separated by ','
* **OAUTH_ID_KEY**
* **OAUTH_TOKEN_URL**
* **OAUTH_AUTHORIZE_URL**
* **OAUTH_USER_URL**
* **OAUTH_USERNAME_PROPERTY** (defaults to `username`)

On manual install, you should set these parameters in the `config.py` file.

Further information can be found in [Python Social Auth’s documentation](https://python-social-auth.readthedocs.io/en/latest/configuration/django.html)
on which Hermine relies.

Users will be created on the fly at authentication by the OAuth server.


## Health check

Hermine provides two test endpoints which you can use in your monitoring system.

`/ping/` always send a 200 response, and can be used to check server availability.

`/ready/` does the same but also tries to connect to Hermine database. It sends a 200 response if it succeeds.
