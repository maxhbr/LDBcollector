<!---  
SPDX-FileCopyrightText: 2022 Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# The Data Model

You can generate [a graph for the data model](_static/hermine_datamodels.svg) with [graphmodels](https://django-extensions.readthedocs.io/en/latest/graph_models.html). 

```
python manage.py graph_models -a -g -o hermine_models.svg
python manage.py graph_models -a > hermine_models.dot
```

## Models for license management

```{eval-rst}
.. automodule:: cube.models.licenses
    :members: 
```



## Models for validation rules

```{eval-rst}
.. automodule:: cube.models.policy
    :members: 
```



## Models for internal product management

```{eval-rst}
.. automodule:: cube.models.products
    :members: 
```

## Models for 3rd party components

```{eval-rst}
.. automodule:: cube.models.components
    :members: 
```
