<!---  
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Installing Hermine

## Getting the code 

To get the code, clone the project with the command: 

```
git clone https://gitlab.com/hermine-project/hermine.git
```

## Installing the dependencies 

Hermine is a simple Django 4 project, using Python 3.8.

It is recommanded to run it in a Python virtual environnement, with the dependencies listed in the [pyproject.toml](https://gitlab.com/hermine-project/hermine/-/blob/main/pyproject.toml) file.

If you use [poetry](https://python-poetry.org/docs/), you can create the virtual environment and install the dependencies with:

```
cd hermine/
poetry install
```

## Running the application



You have to first activate your Python virtual environment. With poetry, it means:
```
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
python hermine/manage.py makemigrations
python hermine/manage.py migrate
```

Then create a user with admin privileges:
```bash
python hermine/manage.py createsuperuser
```

And then launch the django dev server:

```bash
python hermine/manage.py runserver
```

You can then point your browser to [http://127.0.0.1:8080/admin/](http://127.0.0.1:8080/admin/)
and log in as superuser to create new users, or directly to [http://127.0.0.1:8080](http://127.0.0.1:8080) to use the application.


