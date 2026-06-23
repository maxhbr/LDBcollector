# Adding Mappings

Use this checklist when adding or updating an OSS license mapping under `data/`.

## Checklist

1. Choose the canonical identifier first.
   Use the SPDX ID when available. If SPDX has no entry, use the ScanCode LicenseDB key.
2. Name the file exactly like `canonical.id`.
   Example: `GPL-3.0-only.json`.
3. Set `canonical.src` correctly.
   Use `spdx` when the canonical identifier comes from SPDX, otherwise use the source that defines that canonical name.
4. Only use valid alias groups.
   The allowed keys are `spdx`, `scancodeLicensedb`, `pypi`, `osi`, and `custom`.
5. Keep aliases globally unique.
   An alias must not appear in another OSS license file.
6. Put plausible-but-uncertain aliases into `risky`.
   Use this when the alias may resolve here, but the mapping is not deterministic enough for the stable map.
7. Keep version numbers consistent.
   Aliases should match the canonical version unless the data rules explicitly allow broader major-version matching.
8. Set `isMajorVersionOnly` correctly when it applies.
   See [Data Specification](../data/data-specification.md#ismajorversiononly).
9. Run or expect validation.
    Structural problems such as wrong keys, duplicate aliases, invalid sources, or version mismatches are rejected by the validator.

## When to Use Each Alias Group

- `spdx`: SPDX names and identifiers.
- `scancodeLicensedb`: ScanCode names, keys, and `LicenseRef-` identifiers.
- `pypi`: PyPI classifier strings.
- `osi`: Names taken from the OSI license list.
- `custom`: Additional aliases maintained by LicenseLynx.

## Before Opening a Merge Request

- Check the file against [Data Specification](../data/data-specification.md).
- Check the rules in [Data Validation](../data/data-validation.md).
- Keep the change as small as possible.
