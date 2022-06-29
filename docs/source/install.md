<!---  
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Installing Hermine

## Getting last version of code

Clone the project with the command:

```
git clone https://gitlab.com/hermine-project/hermine.git
```

## Development

### Installing the dependencies

Hermine is a simple Django 4 project, using Python 3.8.

You should run Hermin in a Python virtual environnement.
Using [poetry](https://python-poetry.org/docs/), you can create the
virtual environment and install the dependencies with:

```bash
cd hermine/
poetry install
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
and adapt the `mysecrets.py` file you just created.

By default, it just uses a simple SQlite database. To use another database, please refer to [Django's documentation](https://docs.djangoproject.com/en/4.0/topics/install/#get-your-database-running).


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


## Production

### Docker Compose

With [Docker Compose](https://docs.docker.com/compose/), you can run Hermine in
production with just two environment variables and one command line.

You just need to set `HERMINE_SECRET` and `HERMINE_HOST` environment variables before
you can start the containers. The easiest way to do so is to
write it in a .env file.

```bash
# configure secret key
echo "HERMINE_SECRET=RANDOMSTRINGFORSECURITY" > .env
# optional : configure HOST if you use something else than localhost:80
echo "HERMINE_HOST=example.com" >> .env
# start the services in background
docker-compose up -d
```

Hermine should be accessible at `https://example.com`. Caddy automatically sets up
and renew HTTPS certificates.

By default, a superadmin user is
created with `admin / admin` credential. You can update these credentials
from `http://localhost:8080/admin/auth/user/`

### Manual install

You can install yourself dependencies and services for running Hermine.
You need a system running Python 3.8 server. Using a MySQL or PostgreSQL
server rather than the default SQLite is recommended for production.
### OAuth

You can use an OAuth2 server as authentication backend by configuring
OAUTH_CLIENT entry in the mysecrets.py file.

Users will be created on the fly at authentication by the OAuth server.
