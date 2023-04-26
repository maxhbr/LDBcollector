<!---  
SPDX-FileCopyrightText: 2022 Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Developing Hermine

In the following, we assume you have [poetry](https://python-poetry.org/docs/) 
installed in a version 1.2 or later and that you have [installed a local version of Hermine](Install-dev).

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
