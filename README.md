# License Lynx
## Overview
License Lynx is a comprehensive project focused on centralizing various licenses and their aliases into a unified database. 
Additionally, we offer tools to streamline the process of mapping licenses to their canonical names, typically represented by SPDX IDs.

For that, we offer libraries in Python, Java, and TypeScript.

## Folder Structure
The folders **Java**, **Python**, and **TypeScript** are providing libraries to use in code. 
The folder **scripts** contains several useful scripts to update, transform, and verify data.
In the folder **website** we host a static website to introduce the community to the License Lynx project.
<!--- ## Usage --->

## Data source structure
In folder **datasource** all licenses are stored in single json-files. 
The structure of a stored license looks like this:
```json
{
    "canonical": "LGPL-2.0-only",
    "aliases": {
        "spdx": [
            "GNU Library General Public License v2 only",
            "LGPL-2.0"
        ],
        "custom": [],
        "scancode-licensedb": [
            "GNU Library General Public License 2.0",
            "LicenseRef-LGPL-2",
            "LGPL 2.0",
            "LicenseRef-LGPL-2.0",
            "lgpl-2.0"
        ]
    },
    "src": "spdx"
}

```

| ID        | Description                                                                                          |
|-----------|------------------------------------------------------------------------------------------------------|
| canonical | Canonical name for license                                                                           |
| aliases   | Dictionary of sources, where each source is list of aliases of license (e.g. "spdx", "custom", etc.) |
| src       | Source for canonical license name                                                                    |


## Contributing

We welcome contributions from the community to improve this project. If you'd like to contribute, please refer to
our [Contribution Guidelines](https://licenselynx.org/contribution) for detailed instructions on how to get started.

## License

This project is licensed under the terms of the [Apache License, Version 2.0](LICENSE).

Copyright (c) Siemens AG 2024
