<!--
SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>

SPDX-License-Identifier: CC-BY-4.0
-->

# Hermine Project

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)  [![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0) [![REUSE status](https://api.reuse.software/badge/git.fsfe.org/reuse/api)](https://api.reuse.software/info/git.fsfe.org/reuse/api)

Hermine is an Open Source application to manage your SBOMs of Open Source components, their licenses and their respective obligations.

It still is in a very early stage, so please don't expect any stability for the moment.

## Installation

This is a simple Django project, so the safest way to run it is to have a Python 
virtual environnement, with the dependencies listed in the [[pyproject.toml]] file. 

If you use [poetry](https://python-poetry.org/docs/), you create the virtual 
environment by cloning the repo and : 

```
cd hermine-project/
poetry install
```

## Running the application

To run the application, you have to activate your virtual environment.
With poetry, it means: 
```
poetry shell
```

For the first run, you have to create a superuser:
```
python manage.py createsuperuser
```


And then launch the django dev server:

```
cd hermine
python3 manage.py runserver
```
You can then point your browser to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

and log in with admin/admin to create new users

or directly to [http://127.0.0.1:8000](http://127.0.0.1:8000) to use the application.

You can find an in progress documentation at https://hermine-foss.org/ 

