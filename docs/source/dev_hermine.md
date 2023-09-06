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
