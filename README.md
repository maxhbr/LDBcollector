<!--
SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>

SPDX-License-Identifier: CC-BY-4.0
-->

# Hermine Project

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)  [![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0) [![REUSE status](https://api.reuse.software/badge/gitlab.com/hermine-project/hermine)](https://api.reuse.software/info/gitlab.com/hermine-project/hermine)

Hermine is an Open Source application to manage your SBOMs of Open Source components, their licenses and their respective obligations.

It still is in a very early stage, so please don't expect any stability for the moment.

Hermine project's main license is AGPL-3.0-only. Documentation is under CC-BY-4.0.  Some file imported from other projects are licenced under MIT.
You can find the texts of these licences in the  LICENSES folder. Every file should have a licence header.


## Installation

This is a simple Django project, so the safest way to run it is to have a Python 
virtual environnement, with the dependencies listed in the [pyproject.toml](pyproject.toml) file. 

If you use [poetry](https://python-poetry.org/docs/), you create the virtual 
environment by cloning the repo and : 

```
cd hermine/
poetry install
```

## Running the application

Activate your Python virtual environment. With poetry, it means: 
```
poetry shell
```
For the first run, edit your database credentials

```
cp hermine/hermine/mysecrets.default.py hermine/hermine/mysecrets.py 
``` 
and edit the `mysecrets.py` file you just created.


```
python hermine/manage.py makemigrations
python hermine/manage.py migrate
python hermine/manage.py createsuperuser
```

And then launch the django dev server:

```
python3 hermine/manage.py runserver
```
You can then point your browser to [http://127.0.0.1:8080/admin/](http://127.0.0.1:8080/admin/)

and log in as superuser to create new users

or directly to [http://127.0.0.1:8080](http://127.0.0.1:8080) to use the application.

You can find an in progress documentation at https://hermine-foss.org/ 

## OAuth

You can configure OAuth by configuring OAUTH_CLIENT entry in the mysecrets.py file.

Users will be created on the fly at authentication by the OAuth server.
