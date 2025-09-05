# How LicenseLynx Works

## Data Import

LicenseLynx goes through the license lists of SPDX, ScanCode LicenseDB, and OSI and tries to map the licenses with the
SPDX ID, using it as the canonical name.
If a license is not in the SPDX license list, then the key of ScanCode LicenseDB will be used as the canonical name.
The license list of OSI is mainly there to enrich the existing data.

Each license is saved as a JSON file.
This makes editing single licenses much easier and mitigates the risk of editing unaffected licenses.
Also, using JSON files means that there is no need to maintain a database system, making it more open to edits and more
accessible to use.

Before the JSON files are pushed to the main branch, they will be validated to ensure the following criteria are met:

1. The JSON filename must be equal to the canonical name.
2. Each alias must be unique globally.
3. If the source of a license file is SPDX, the canonical name must exist in the SPDX license list.
4. No empty fields are allowed except in `aliases` and the `custom` field.
5. The length of an entry must not exceed 100 characters.
6. A canonical identifier must not include any of the forbidden characters:
   `{"#", "$", "%", "=", "[", "]", "?", "<", ">", ":", "/", "\\", "|", "*", " "}`.
7. The version between canonical identifier and aliases must be equal.

## Data Structure

All licenses are stored in single JSON files within the **data** folder. Each file contains the canonical name, its
aliases with their sources, and the source of the canonical name. For example:

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
  "src": "spdx",
  "rejected": [],
  "risky": []
}
```

## Quotes Handling for Aliases

When an alias contains a word or phrase enclosed in quotation marks during the license file update process from data
sources, it receives special handling.
If the quotation marks used are not the standard single quote (`'`) or double quote (`"`), but rather another Unicode
quotation mark (see [the list below](#list-of-unicode-quotes)), they are replaced with the single quote.
Additionally, if an alias with a single quote exists, a version with double quotes will be added to the `custom` aliases
list, and vice versa.

### List of Unicode Quotes

```python
quote_characters = [
    # Single quotes
    "\u2018",  # LEFT SINGLE QUOTATION MARK ‘
    "\u2019",  # RIGHT SINGLE QUOTATION MARK ’
    "\u201A",  # SINGLE LOW-9 QUOTATION MARK ‚
    "\u201B",  # SINGLE HIGH-REVERSED-9 QUOTATION MARK ‛
    "\u2032",  # PRIME (often used as an apostrophe) ′
    "\uFF07",  # FULLWIDTH APOSTROPHE ＇
    # Double quotes
    "\u201C",  # LEFT DOUBLE QUOTATION MARK “
    "\u201D",  # RIGHT DOUBLE QUOTATION MARK ”
    "\u201E",  # DOUBLE LOW-9 QUOTATION MARK „
    "\u201F",  # DOUBLE HIGH-REVERSED-9 QUOTATION MARK ‟
    "\u2033",  # DOUBLE PRIME ″
    "\u00AB",  # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK «
    "\u00BB",  # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK »
    "\uFF02",  # FULLWIDTH QUOTATION MARK ＂
]
```

## Usage in Code

LicenseLynx provides libraries for Python, Java, and TypeScript, making it easy to map licenses programmatically.  
It is also possible to use a Web API.
The JSON license files are merged in the pipeline to single JSON file with all the mappings.
To find out how to use the libraries, go to [Usage](usage.md).
