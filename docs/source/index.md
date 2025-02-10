<!---
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr>
SPDX-License-Identifier: CC-BY-4.0
-->

# Welcome to Hermine's documentation

:::{warning}
As the application itself, this documentation is very much a work in progress.
:::

The documentation is created with [Sphinx](https://www.sphinx-doc.org/en/master/), and written (mostly) in [Markdown](https://www.markdownguide.org/basic-syntax), thanks to [MyST](https://myst-parser.readthedocs.io/en/latest/sphinx/index.html).
The [MyST documentation](https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html) will guide you through the sphinx-specific directives in Markdown.
Some options like [code fences using colors](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#code-fences-using-colons) and [field lists](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#field-lists) have been activated.

You will find the source of this documentation in the `docs/source` folder of the [repo](https://gitlab.com/hermine-project/hermine/-/tree/main/docs).

To build it locally, you must first install the application locally and configure it [as explained in the installation page](install.md#manual-install).
Dont't forget to activate your poetry env with :
```bash
poetry env activate
```
and executing the displayed command.

Then you can actually build the html pages:
```bash
sphinx-build -b html docs/source docs/build/html
```
Once it's build, you can visualize the pages in your browser using Python's web server module:
```bash
python -m http.server --directory docs/build/html
```

This documentation is published under the CC-BY-4.0 license.

```{toctree}
---
maxdepth: 2
caption: Contents
---
use_hermine
dev_hermine
```


## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
