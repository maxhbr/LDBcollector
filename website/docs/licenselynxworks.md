# How LicenseLynx Works

## Data import

LicenseLynx goes through the license lists of SPDX, ScanCode LicenseDB, and OSI and tries to map the licenses with the SPDX ID and uses it as the cannonical name.
If a license is not in the SPDX license list, then the key of ScanCode LicenseDB will be used as cannanonical name.
The license list of OSI is mainly there to enrich the existing data.

Each license is saved as a JSON file.
This makes editing single licenses much easier and mitigates the risk of editing not affected licenses.
Also, using JSON files means that there is no need to maintain a database system which makes it more open to edit changes and more accessible to use.

Before the JSON files are pushed to the main branch, the files will be validated, so that following criterias are met:

1. JSON filename must be equal to the canonical name
2. Each aliases must be unique globally
3. If the source of an license file is SPDX, canonical name must exist in the SPDX license list
4. No empty fields are allowed except in ``aliases`` the ``custom`` field
5. The length of an entry must not be longer than 100 characters
6. An entry must not include one of the forbidden characters which are ``{"#", "$", "%", "=", "[", "]", "?", "<", ">", ":", "/", "\\", "|", "*", " "}``


## Data Structure

All licenses are stored in single JSON files within the **data** folder. Each file contains the canonical name, its aliases with their sources, and the source of the canonical name. For example:

```json
{
    "canonical": "LGPL-2.0-only",
    "aliases": [
        {
            "spdx": [
                "GNU Library General Public License v2 only",
                "LGPL-2.0"
            ],
            "custom": []
        }
    ],
    "src": "spdx"
}
```

## Usage in Code

LicenseLynx provides libraries for Python, Java, and TypeScript, making it easy to map licenses programmatically.  
It also possible to use an Web API.
The JSON license files are merged in the pipeline to single JSON file with all the mappings.
To find out how to use the libraries, go to [Usage](usage.md).
