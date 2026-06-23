# How LicenseLynx Works

LicenseLynx turns many license names into deterministic canonical identifiers.

It collects names from external sources, stores them as small JSON files, and merges them into the lookup data used by the libraries and the public JSON endpoint.

## Canonical Identifiers

LicenseLynx goes through the license lists of SPDX, ScanCode LicenseDB, and OSI and tries to map the licenses with the
SPDX ID, using it as the canonical name.
If a license is not in the SPDX license list, then the key of ScanCode LicenseDB will be used as the canonical name.
The license list of OSI is mainly there to enrich the existing data.

## Source Files

Each license is saved as a JSON file.
This makes editing single licenses much easier and mitigates the risk of editing unaffected licenses.
Also, using JSON files means that there is no need to maintain a database system, making it more open to edits and more
accessible to use.

Organization-specific mappings use the same structure, but live under `data/orgs/<org>/`.

## Build Output

Before the JSON files are pushed to the main branch, they are validated for filename consistency, alias uniqueness, source correctness, version consistency, and organization-specific constraints.
See [Data Validation](data/data-validation.md) for the full list.

During the build pipeline, all individual files are merged into a single `merged_data.json` that separates aliases into:

- a **stable map**
- a **risky map**
- any **organization-specific maps**

For the source-specific update scripts that populate the data before this merge step, see [Automated Data Retrieval](data/data-retrieval.md).

All licenses are stored in single JSON files within the **data** folder. For example:

```json
{
  "canonical": {
    "id": "LGPL-2.0-only",
    "src": "spdx"
  },
  "aliases": {
    "spdx": [
      "GNU Library General Public License v2 only",
      "LGPL-2.0"
    ],
    "custom": [],
    "scancodeLicensedb": [
      "GNU Library General Public License 2.0",
      "LicenseRef-LGPL-2",
      "LGPL 2.0",
      "LicenseRef-LGPL-2.0",
      "lgpl-2.0"
    ]
  },
  "rejected": [],
  "risky": []
}
```

For the full field reference and merged format, see the [Data Specification](data/data-specification.md).

## Related Pages

- [Data Quality](data/data-quality.md)
- [Data Specification](data/data-specification.md)
- [Automated Data Retrieval](data/data-retrieval.md)
- [Matching Behavior](data/matching-behavior.md)
- [Data Validation](data/data-validation.md)
- [Risky Mappings](data/risky-mappings.md)
