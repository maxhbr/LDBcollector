# Data Specification

LicenseLynx stores license data in two formats: **individual license files** (source of truth, editable) and a **merged mapping file** (
generated, used by libraries and the web endpoint).

## Individual License Files

Each license has its own JSON file in the `data/` folder, named after its canonical identifier.

```json
{
    "canonical": {
        "id": "GPL-3.0-only",
        "src": "spdx"
    },
    "aliases": {
        "spdx": [
            "GNU General Public License v3.0 only",
            "GPL-3.0"
        ],
        "custom": [
            "GENERAL PUBLIC LICENSE, version 3 (GPL-3.0)",
            "GPL v3"
        ],
        "osi": [
            "GNU General Public License, Version 3.0"
        ],
        "scancodeLicensedb": [
            "GNU General Public License 3.0",
            "gpl-3.0"
        ],
        "pypi": [
            "License :: GNU General Public License v3",
            "License :: OSI Approved :: GPLv3"
        ]
    },
    "rejected": [],
    "risky": [
        "gpl3"
    ],
    "isMajorVersionOnly": true
}
```

### Fields

| Field                       | Type       | Description                                                                                                |
|-----------------------------|------------|------------------------------------------------------------------------------------------------------------|
| `canonical`                 | `object`   | Contains the canonical `id` and its `src`.                                                                 |
| `canonical.id`              | `string`   | The canonical license identifier. Must equal the filename (without `.json`).                               |
| `canonical.src`             | `string`   | Origin of the canonical name (see [Data Sources](#data-sources)).                                          |
| `aliases`                   | `object`   | Known alternative names, grouped by source key.                                                            |
| `aliases.spdx`              | `string[]` | Names from the SPDX license list (full names, deprecated IDs).                                             |
| `aliases.scancodeLicensedb` | `string[]` | Names from ScanCode LicenseDB (keys, full names, `LicenseRef-` identifiers).                               |
| `aliases.pypi`              | `string[]` | PyPI classifier strings (e.g., `"License :: OSI Approved :: MIT License"`).                                |
| `aliases.osi`               | `string[]` | Names from the OSI license list.                                                                           |
| `aliases.custom`            | `string[]` | Community-contributed aliases. This is where your contributions go.                                        |
| `rejected`                  | `string[]` | Aliases that automated sources (SPDX, ScanCode, OSI) would otherwise pull in, but map incorrectly. Listing them here prevents re-import on update. Strings that no automated source imports don't need to be listed. |
| `risky`                     | `string[]` | Ambiguous strings that could plausibly map here but lack certainty. Only returned when the caller opts in. |
| `isMajorVersionOnly`        | `boolean`  | Whether the canonical identifier has only a major version, relevant for the version matching validation.   |

For validation rules applied to these files, see [Data Validation](data-validation.md).
For how external sources populate these alias groups, see [Automated Data Retrieval](data-retrieval.md).

### isMajorVersionOnly

This flag is only relevant for canonical identifiers with exactly one version token such as `Apache-2.0` or `GPL-3.0-only`.

- `true` means this major version is unique within its license family.
- `false` means there are multiple canonical identifiers with the same major version in that family.

The validator determines this by grouping licenses by base name and comparing their major version numbers. This affects how strict the alias version matching can be.

## Merged Mapping File

The build pipeline merges all individual files into a single `merged_data.json` with the following structure:

```json
{
    "stableMap": {
        "MIT": {
            "id": "MIT",
            "src": "spdx"
        },
        "MIT License": {
            "id": "MIT",
            "src": "spdx"
        },
        "mit": {
            "id": "MIT",
            "src": "scancode-licensedb"
        },
        ...
    },
    "riskyMap": {
        "gpl3": {
            "id": "GPL-3.0-only",
            "src": "spdx"
        },
        ...
    },
    "siemens": {
        "SISL-1.4": {
            "id": "SISL-1.4",
            "src": "siemens"
        },
        ...
    }
}
```

### Top-Level Keys

| Key                       | Description                                                              |
|---------------------------|--------------------------------------------------------------------------|
| `stableMap`               | All aliases from every license file. This is the default lookup target.  |
| `riskyMap`                | All `risky` entries from every license file. Only queried when opted in. |
| `<org>` (e.g., `siemens`) | Organization-specific license mappings.                                  |

### Entry Format

Each entry in any map is keyed by the alias string and contains:

| Field | Type     | Description                                              |
|-------|----------|----------------------------------------------------------|
| `id`  | `string` | The canonical license identifier this alias resolves to. |
| `src` | `string` | The source of the canonical name.                        |

## Data Sources

| Source             | `src` value            | Description                                                                               |
|--------------------|------------------------|-------------------------------------------------------------------------------------------|
| SPDX License List  | `"spdx"`               | The primary source. SPDX ID is used as canonical name.                                    |
| ScanCode LicenseDB | `"scancode-licensedb"` | Fallback when no SPDX entry exists. ScanCode key becomes canonical name.                  |
| OSI License List   | N/A                    | Used to enrich existing entries with additional aliases. Does not define canonical names. |
| PyPI Classifiers   | N/A                    | License classifier strings from PyPI packages. Does not define canonical names.           |
| Custom/Community   | `"custom"`             | Community-contributed aliases added to the `custom` list.                                 |
| Organizations      | e.g., `"siemens"`      | Organization-maintained internal licenses.                                                |

For the retrieval scripts behind the automated sources, see [Automated Data Retrieval](data-retrieval.md).
