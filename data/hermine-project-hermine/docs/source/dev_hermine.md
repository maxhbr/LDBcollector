<!---  
SPDX-FileCopyrightText: 2022 Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Developing Hermine

In order to run Hermine in development mode,
follow manual installation instructions in the [installation guide](install.md)
up to the server part.

Then, use the following commands to run the development server:

```bash
# inside poetry environment
python hermine/manage.py runserver
```

To run the tests, use the following command:

```bash
# inside poetry environment
python hermine/manage.py test
```

To build front modules, use the following command:

```bash
npm run install
npm run watch # watch for changes and rebuild
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

## Specific aspects

We document here the Hermine-specific aspects of the code. 
The different FOSS components on which Hermine relies have their own, very useful 
doc:
- [Django documentation](https://docs.djangoproject.com)
- [Django REST Framework documentation](https://www.django-rest-framework.org/)
- [Django filter](https://django-filter-model.readthedocs.io/)  
- [Pacakge URL (Purl) specification](https://github.com/package-url/purl-spec) 
and its [Python library](https://github.com/package-url/packageurl-python) 

```{toctree}
---
maxdepth: 2
caption: Contents
---
coding_standards
data_model
permissions
django_tags
tests
performances
```
