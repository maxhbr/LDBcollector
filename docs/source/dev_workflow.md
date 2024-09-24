<!---  
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Basic development workflow 


## Standard install


In order to run Hermine in development mode, follow manual installation instructions in the [installation guide](install.md#manual-install).

Then, use the following commands to run the development server:

```bash
# inside poetry environment
python hermine/manage.py runserver
```

To run the tests, use the following command:

```bash
# inside poetry environment
cd hermine
python manage.py test
```


## Working with DevContainer

You can also run Hermine inside a [DevContainer](https://containers.dev/).

It allows to develop inside a container, in a described and clean environnment. You need to find how to integrate it to your IDE.

The PostCreate command will do the database migrations, you need to create your superuser and run the server. You also need to create your config file from default one.
```bash
cp hermine/hermine/config.default.py hermine/hermine/config.py
poetry run python hermine/manage.py createsuperuser
poetry run python hermine/manage.py runserver
```

