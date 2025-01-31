# How LicenseLynx Works

## Data Import

LicenseLynx goes through the license lists of SPDX, ScanCode LicenseDB, and OSI and tries to map the licenses with the SPDX ID, using it as the canonical name.
If a license is not in the SPDX license list, then the key of ScanCode LicenseDB will be used as the canonical name.
The license list of OSI is mainly there to enrich the existing data.

Each license is saved as a JSON file.
This makes editing single licenses much easier and mitigates the risk of editing unaffected licenses.
Also, using JSON files means that there is no need to maintain a database system, making it more open to edits and more accessible to use.

Before the JSON files are pushed to the main branch, they will be validated to ensure the following criteria are met:

1. The JSON filename must be equal to the canonical name.  
2. Each alias must be unique globally.  
3. If the source of a license file is SPDX, the canonical name must exist in the SPDX license list.  
4. No empty fields are allowed except in `aliases` and the `custom` field.  
5. The length of an entry must not exceed 100 characters.  
6. An entry must not include any of the forbidden characters: `{"#", "$", "%", "=", "[", "]", "?", "<", ">", ":", "/", "\\", "|", "*", " "}`.  

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
