# Automated Data Retrieval

LicenseLynx uses Python scripts in `scripts/src/update/` to pull license data from external sources and update the individual JSON files in `data/`.

## Automated Sources

| Source | Script | Alias key | What it adds |
|--------|--------|-----------|--------------|
| SPDX License List | `SpdxDataUpdate.py` | `spdx` | SPDX names, deprecated identifiers, and SPDX exception data where applicable |
| ScanCode LicenseDB | `ScancodeLicensedbDataUpdate.py` | `scancodeLicensedb` | ScanCode keys, names, and `LicenseRef-` identifiers |
| OSI License List | `OsiDataUpdate.py` | `osi` | OSI names, alternative names, and URL-derived identifiers |

## Running the Update Scripts

The update entry point is exposed through Poetry from the `scripts/` project.

```bash
poetry run data_update --spdx --scancode --osi
```

Each flag runs independently:

- `--spdx`
- `--scancode`
- `--osi`

After the selected updates run, the major-version metadata update and the validation step run automatically.

## Shared Update Behavior

All update scripts share the same base logic:

- aliases are normalized before they are written
- quote variants are added to `custom` automatically
- aliases already listed in `rejected` or `risky` are skipped
- alias lists are sorted alphabetically

## PyPI and Custom Aliases

Not every alias group is maintained by the current automated update pipeline.

`pypi` stores PyPI trove classifier strings such as `License :: OSI Approved :: MIT License`. These entries were added in bulk and are still useful because those classifier strings remain relevant for mapping package metadata. There is no recurring PyPI update script in `scripts/src/update/`.

`custom` contains manually maintained aliases plus quote-swapped variants generated during automated updates.

## Related Pages

- [How LicenseLynx Works](../licenselynxworks.md)
- [Data Specification](data-specification.md)
- [Data Validation](data-validation.md)
- [Adding Mappings](../contributing/adding-mappings.md)
