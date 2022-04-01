<!---  
SPDX-FileCopyrightText: Hermine team <hermine@inno3.fr> 
SPDX-License-Identifier: CC-BY-4.0
-->

# Welcome to Hermine's documentation

:::{warning}
As the application itself, this documentation is very much a work in progress.
:::

The documentation is created with Sphinx, and written (mostly) in [Markdown](https://www.markdownguide.org/basic-syntax), thanks to [MyST](https://myst-parser.readthedocs.io/en/latest/sphinx/index.html).
The [MyST documentation](https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html) will guide you through the sphinx-specficic directives in Markdown. Some options like [code fences using colons](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#code-fences-using-colons) and [field lists](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#field-lists) have been activated. 

You will find the source of this documentation in the `docs/source` folder of the repo.

To build it locally, install the dev dependencies of the project and use the command:

```bash
sphinx-build -b html docs/source docs/build/html
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
