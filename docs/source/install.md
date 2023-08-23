<!---  
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Installing Hermine

## Docker Compose

Hermine provides a [Docker Compose](https://docs.docker.com/compose/) configuration with the
following services:
* a PostgreSQL database
* a [Caddy](https://caddyserver.com/) server to
[serve static files](https://docs.djangoproject.com/en/4.1/howto/static-files/deployment/)
and proxy other requests to gunicorn
* a [gunicorn](https://gunicorn.org/) server for the Python backend

Two profiles are available :
* an `https` profile where Caddy is configured with automatic HTTPS. It can easily be
deployed on a VPS.
* a `localhost` profile to use Hermine on a local machine or behind a reverse proxy (not suited for development) 

Configuration is made through a [`.env` file](https://github.com/bkeepers/dotenv) which should be
placed at the root of the project.

By default, a superadmin user is created with `admin / admin` credential.
You can update these credentials from `http://example.com/admin/auth/user/`.

In case you need to access the `django-admin` tool from outside Docker, you should use :
`docker exec -it hermine_django_1 /opt/hermine/manage.py`

### HTTPS profile

You just need to set `HERMINE_SECRET` and `HERMINE_HOST` environment variables before
you can start the containers. The easiest way to do so is to
write it in a .env file.

```bash
# configure secret key
echo "HERMINE_SECRET=RANDOMSTRINGFORSECURITY" > .env
# optional : configure HOST if you use something else than localhost:80
echo "HERMINE_HOST=example.com" >> .env
# start the services in background
docker-compose --profile https up -d
```

Hermine should be accessible at `https://example.com`. Caddy automatically sets up
and renew HTTPS certificates.

To update your instance : 

```bash
cd hermine/
git switch main && git pull
docker-compose --profile https up -d --build
```

### Localhost profile

You must set `PORT` insted of `HERMINE_HOST` variable.

```bash
# configure secret key
echo "HERMINE_SECRET=RANDOMSTRINGFORSECURITY" > .env
# configure port
echo "PORT=9000" >> .env
# start the services in background
docker-compose --profile localhost up -d
```

(Install-dev)=
## Manual install

### Downloading the source code

You can download latest releases from [Hermine releases page](https://gitlab.com/hermine-project/hermine/-/releases)
or clone latest development version from [GitLab](https://gitlab.com/hermine-project/hermine/-/tree/main).

You can also use git to clone a specific version :
    
```bash
git clone --branch v0.0.1 https://gitlab.com/hermine-project/hermine.git
```

Major versions changes mean breaking changes, either in the installation configuration or in the API.
You can find more information in [CHANGELOG.md](https://gitlab.com/hermine-project/hermine/-/blob/main/CHANGELOG.md).

For minor or patch versions, it should be safe to update your instance by pulling the latest tag from the repository or
downloading from the release page.

### Install python dependencies

You should run Hermine in a Python virtual environnement.
Using [poetry](https://python-poetry.org/docs/), you can create the
virtual environment and install the dependencies with:

```bash
cd hermine/
poetry install
```

### Install and build front modules

```bash
npm install
# or if you do not want to edit the front code
npm run build
```

### Configure your instance

Before the first run, you have to create a `config.py` file in the `hermine/hermine/` directory.

```
cp hermine/hermine/config.default.py hermine/hermine/config.py
```

Update the database structure and create a superuser :
```
# activate poetry shell
poetry shell

# create database structure
python hermine/manage.py migrate

# create a superuser
python hermine/manage.py createsuperuser
```

### Run the server

How you want to serve Hermine is up to you. You should be familiar with WSGI servers and reverse proxies. You can find more information in
[Django documentation](https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/gunicorn/).

A typical installation is :

* Gunicorn or another WSGI server (running Hermine's `wsgi.py`) 
* NGinx to serve static files and proxy other requests to Gunicorn

Hermine is not different from any other Django application. You can find more information in [Django documentation](https://docs.djangoproject.com/en/4.1/howto/deployment/).

#### Static files

Static files should be served by your web server. After
install, you must run `collectstatic` to copy static files to the `static`
directory (or any other configured in `config.py`).

```bash
python hermine/manage.py collectstatic
```

You can find more information in [Django documentation](https://docs.djangoproject.com/en/4.1/howto/static-files/deployment/).

## OAuth

You can use an OAuth2 server as authentication backend by uncommenting and 
adjusting  the `OAUTH_CLIENT` entry in your `config.py` file. When using Docker, 
these elements have to be set in your `.env` file.  Further information
can be found in [Python Social Auth’s documentation](https://python-social-auth.readthedocs.io/en/latest/configuration/django.html) 
on which Hermine relies.

Users will be created on the fly at authentication by the OAuth server.


## Health check

Hermine provides two test endpoints which you can use in your monitoring system.

`/ping` always send a 200 response, and can be used to check server availability.

`/ready` do the same but also tries to connect to Hermine database. It sends a 200 response if it succeeds.

