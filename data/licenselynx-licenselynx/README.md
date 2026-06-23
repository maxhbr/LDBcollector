![total mappings](website/badges/total-mappings.svg)
[![GitHub Tag](https://img.shields.io/github/v/tag/licenselynx/licenselynx)](https://github.com/licenselynx/licenselynx/releases/latest)
[![license](https://img.shields.io/github/license/licenselynx/licenselynx)](LICENSE)

[![python coverage](https://img.shields.io/codecov/c/github/licenselynx/licenselynx/main?flag=python&label=python%20coverage)](https://codecov.io/gh/licenselynx/licenselynx)
[![java coverage](https://img.shields.io/codecov/c/github/licenselynx/licenselynx/main?flag=java&label=java%20coverage)](https://codecov.io/gh/licenselynx/licenselynx)
[![go coverage](https://img.shields.io/codecov/c/github/licenselynx/licenselynx/main?flag=go&label=go%20coverage)](https://codecov.io/gh/licenselynx/licenselynx)
[![typescript coverage](https://img.shields.io/codecov/c/github/licenselynx/licenselynx/main?flag=typescript&label=typescript%20coverage)](https://codecov.io/gh/licenselynx/licenselynx)
[![scripts coverage](https://img.shields.io/codecov/c/github/licenselynx/licenselynx/main?flag=scripts&label=scripts%20coverage)](https://codecov.io/gh/licenselynx/licenselynx)

[![python pipeline](https://github.com/licenselynx/licenselynx/actions/workflows/python.yaml/badge.svg)](https://github.com/licenselynx/licenselynx/actions/workflows/python.yaml)
[![java pipeline](https://github.com/licenselynx/licenselynx/actions/workflows/java.yaml/badge.svg)](https://github.com/licenselynx/licenselynx/actions/workflows/java.yaml)
[![go pipeline](https://github.com/licenselynx/licenselynx/actions/workflows/go.yaml/badge.svg)](https://github.com/licenselynx/licenselynx/actions/workflows/go.yaml)
[![typescript pipeline](https://github.com/licenselynx/licenselynx/actions/workflows/typescript.yaml/badge.svg)](https://github.com/licenselynx/licenselynx/actions/workflows/typescript.yaml)
[![scripts pipeline](https://github.com/licenselynx/licenselynx/actions/workflows/scripts.yaml/badge.svg)](https://github.com/licenselynx/licenselynx/actions/workflows/scripts.yaml)
[![data pipeline](https://github.com/licenselynx/licenselynx/actions/workflows/data.yaml/badge.svg)](https://github.com/licenselynx/licenselynx/actions/workflows/data.yaml)

# LicenseLynx 

## Overview

LicenseLynx is a project focused on deterministically map unknown or ambiguous license names and their canonical license names.
Additionally, we offer libraries for Python, Java, Go, and TypeScript to streamline the process of mapping licenses to their canonical names,
typically represented by SPDX IDs.

## Folder Structure

The folders **Go**, **Java**, **Python**, and **TypeScript** are providing libraries to use in code.
The folder **scripts** contains several useful scripts to update, transform, and verify data.
In the folder **website** we host a static website to introduce the community to the LicenseLynx project.
The folder **data/orgs/** contains organization-specific (internal) license mappings, organized by organization name (e.g., `data/orgs/siemens/`).

## Data structure

In folder **data** all licenses are stored in their own json-files.
The structure of a stored license looks like this:

```json
{
    "canonical": {
        "id": "BSD-3-Clause",
        "src": "spdx"
    },
    "aliases": {
        "spdx": [
            "BSD 3-Clause \"New\" or \"Revised\" License"
        ],
        "custom": [
            "3-Clause BSD",
            "3-Clause BSD License",
            "EDL 1.0",
            "Modified BSD License",
            "new BSD",
            "BSD 3-Clause Revised"
        ],
        "osi": [
            "BSD-3",
            "Revised BSD License"
        ],
        "scancodeLicensedb": [
            "bsd-new",
            "LicenseRef-scancode-libzip"
        ]
    },
    "rejected": [],
    "risky": []
}

```

| ID        | Description                                                                                          |
|-----------|------------------------------------------------------------------------------------------------------|
| canonical | JSON Object for canonical identifier `id` and the source `src` where this information comes from     |
| aliases   | Dictionary of sources, where each source is list of aliases of license (e.g. "spdx", "custom", etc.) |
| rejected  | List of rejected aliases                                                                             |
| risky     | List of risky aliases                                                                                |

### Organization Licenses

Organization-specific (internal) license files are stored in `data/orgs/<org_name>/` and use the same JSON format as OSS license files. The key difference is that `canonical.src` must match the organization folder name (e.g., `"siemens"` for files in `data/orgs/siemens/`).

There must be no overlap between OSS and organization license identifiers. Organization licenses are isolated from the main dataset and only resolve when explicitly requested via the `org` parameter in the library `map()` functions.

### Adding Your Organization

To have LicenseLynx support your organization's internal licenses, follow these steps:

1. **Create a folder** for your organization under `data/orgs/` using a lowercase name, e.g. `data/orgs/myorg/`.
2. **Add license JSON files** for each internal license. Each file must follow the same format as OSS license files. For example, a file `data/orgs/myorg/MYORG-ISL-1.0.json` would look like:

    ```json
    {
        "canonical": {
            "id": "MYORG-ISL-1.0",
            "src": "myorg"
        },
        "aliases": {
            "custom": [
                "My Org Inner Source License 1.0",
                "MYORG ISL 1.0"
            ]
        },
        "rejected": [],
        "risky": []
    }
    ```

    Key rules:
    - `canonical.src` must match the organization folder name exactly.
    - `canonical.id` must match the filename without the `.json` extension.
    - Aliases must use the `custom` key.
    - Canonical IDs must be at most 100 characters and must not contain forbidden characters (`#$%=[]?<>:/\|*` or spaces).

3. **Ensure no overlap** between your organization's license identifiers/aliases and existing OSS license data. The CI pipeline will reject any collisions.
4. **Submit a Pull Request**. The data validation pipeline will automatically verify the structure, naming, and uniqueness constraints of your contribution.
5. **Library update**. In the same PR, the `Organization` enum in the Python, Java, and TypeScript libraries must be updated to include your new organization.
6. **Verify your identity**. To confirm that you are a valid representative of the organization, you must either have a verified email address from that organization or have the organization listed officially on your GitHub profile.


Once added, organization licenses can be resolved by passing the `org` parameter to the library `map()` functions.

## Data Quality

With LicenseLynx we aim to have a deterministic mean of license mappings.
For more details, head to our [website](https://licenselynx.org/data/data-quality) to find out more.

## Contributing

We welcome contributions from the community to improve this project. If you'd like to contribute, please refer to
our [Contribution Guidelines](https://licenselynx.org/contribution) for detailed instructions on how to get started.

## License

This project is licensed under the [BSD 3-Clause "New" or "Revised" License](LICENSE) (SPDX-License-Identifier: BSD-3-Clause).

Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
