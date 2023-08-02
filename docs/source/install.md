<!---  
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Installing Hermine
(Install-dev)=
## Development

### Getting last version of code

Clone the project with the command:

```
git clone https://gitlab.com/hermine-project/hermine.git
```

### Installing the dependencies

You should run Hermine in a Python virtual environnement.
Using [poetry](https://python-poetry.org/docs/), you can create the
virtual environment and install the dependencies with:

```bash
cd hermine/
poetry install
```

### Build front modules

```bash
npm install
npm run build

# or for development
npm run dev
```

### Running the server

You have to first activate your Python virtual environment. With poetry, it means:
```bash
poetry shell
```
For the first run, you have to edit your database credentials:

```
cp hermine/hermine/mysecrets.default.py hermine/hermine/mysecrets.py
```
and adapt the `mysecrets.py` file you just created: you must *a minima* declare a value for `SECRET_KEY` (see [Django's documentation](https://docs.djangoproject.com/en/4.2/ref/settings/#secret-key)).

By default, it uses a simple SQlite database. To use another database, please refer to [Django's documentation](https://docs.djangoproject.com/en/4.0/topics/install/#get-your-database-running).


Create the database structure:
```bash
python hermine/manage.py migrate
```

Then create a user with admin privileges:
```bash
python hermine/manage.py createsuperuser
```

And then launch the django development server:

```bash
python hermine/manage.py runserver
```

You can then point your browser to [http://127.0.0.1:8080/admin/](http://127.0.0.1:8080/admin/)
and log in as superuser to create new users, or directly to [http://127.0.0.1:8080](http://127.0.0.1:8080) to use the application.

For production, you should use an uWSGI server rather than the Django development
server. Refer to
the [Django documentation](https://docs.djangoproject.com/fr/4.0/howto/deployment/).


## Docker Compose

Hermine provides a [Docker Compose](https://docs.docker.com/compose/) configuration with the
following services :
* a PostgreSQL database
* a [Caddy](https://caddyserver.com/) server to
[serve static files](https://docs.djangoproject.com/en/4.1/howto/static-files/deployment/)
and proxy other requests to gunicorn
* a [gunicorn](https://gunicorn.org/) server for the Python backend

Two profiles are available :
* an `https` profile where Caddy is configured with automatic HTTPS. It can easily be
deployed on a VPS.
* a `localhost` profile to use Hermine on a local machine (but not suited for development, where
you should not use Docker)

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
# disable debug mode
echo "PRODUCTION=true" >> .env
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
# disable debug mode
echo "PRODUCTION=true" >> .env
# start the services in background
docker-compose --profile localhost up -d
```

## Manual production install

You can install yourself dependencies and services for running Hermine.
You need a system running Python 3.8 server. Using a PostgreSQL
server rather than the default SQLite is recommended for production.

## OAuth

You can use an OAuth2 server as authentication backend by uncommenting and 
adjusting  the `OAUTH_CLIENT` entry in your `mysecrets.py` file. When using Docker, 
these elements have to be set in your `.env` file.  Further information
can be found in [Python Social Auth’s documentation](https://python-social-auth.readthedocs.io/en/latest/configuration/django.html) 
on which Hermine relies.

Users will be created on the fly at authentication by the OAuth server.


## Health check

Hermine provides two test endpoints which you can use in your monitoring system.

`/ping` always send a 200 response, and can be used to check server availability.

`/ready` do the same but also tries to connect to Hermine database. It sends a 200 response if it succeeds.


## Display version

You can display a version in the footer, using your own versionning convention.

You need to add a file in the application path containing one line with the version you want to display, and set this variable in your settings (mysecrets.py) : 
```python
# Path to the current version to be displayed in the footer 
VERSION_FILE_PATH = "hermine/hermine/VERSION.txt"
```
For example, you can generate your file by adding in the .gitlabci building the Docker image :
```bash
LAST_COMMIT=$(git log -1 --pretty="%ad")
echo "Last Updated: $LAST_COMMIT ($GITLAB_UPSTREAM_BRANCH)" > hermine/VERSION.txt
```
