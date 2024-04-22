<!---  
SPDX-FileCopyrightText: 2022 Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Coding standards

## Developer Certificate of Origin

Before pushing code or content to the project's repo, you have to check that you 
own the appropriate rights to publish it under the project's licenses, and approve 
the terms of the [Developer Certificate of Origin version 1.1](https://developercertificate.org/). 
To do so, you have to sign-off your commits by adding the `--signoff` option to 
your `git commit` commands.

## REUSE standard

We try to follow the [REUSE standard](https://reuse.software/). So if you add a new file, please add also the appropriate headers following the template:

```
# SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
# SPDX-License-Identifier: AGPL-3.0-only 
```

## Code linting

We use [Black](https://pypi.org/project/black/) for harmonising code formatting, 
[Ruff](https://github.com/charliermarsh/ruff) for linting and 
[DjHTML](https://github.com/rtts/djhtml) for indenting Django Templates.

## Naming conventions

We try to stay consistent in naming Django models, views,
route names and so on. Here are some example for
a hypothetical `ObjectName` model and its associated views:

```python
# urls.py

urlpatterns = [
    # ...
    path("objectnames/", views.ObjectNameListView.as_view(), name="objectname_list"),
    path("objectnames/new/", views.ObjectNameCreateView.as_view(), name="objectname_create"),
    path("objectnames/<int:pk>/", views.ObjectNameDetailView.as_view(), name="objectname_detail"),
    path("objectnames/<int:pk>/edit/", views.ObjectNameUpdateView.as_view(), name="objectname_update"),
    path("objectnames/<int:pk>/delete/", views.ObjectNameDeleteView.as_view(), name="objectname_delete"),
    # ...
]


# views.py
class ObjectNameDetailView(DetailView):
    model = ObjectName
    template_name = "objectname_detail.html"

class ObjectNameListView(ListView):
    model = ObjectName
    template_name = "objectname_list.html"

class ObjectNameCreateView(CreateView):
    model = ObjectName
    template_name = "objectname_create.html"  # or default "objectname_form.html"

class ObjectNameUpdateView(UpdateView):
    model = ObjectName
    template_name = "objectname_update.html" # or default "objectname_form.html"
    
class ObjectNameDeleteView(DetailView):
    model = ObjectName
    template_name = "objectname_confirm_delete.html" # this is django default

```

## Commit messages

It would be nice to try to follow the [Conventional Commits standards](https://www.conventionalcommits.org/en/v1.0.0/)

