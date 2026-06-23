# Data Validation

Before data is merged, LicenseLynx validates both the OSS license files and the organization-specific license files.

## Core Checks

These checks apply to every license file:

1. Filename must match `canonical.id`.
2. Aliases must be unique globally.
3. `canonical.src` must be valid.
4. If `canonical.src` is `spdx`, `canonical.id` must exist in the SPDX license or exception lists.
5. `aliases` must only use these keys: `spdx`, `scancodeLicensedb`, `pypi`, `osi`, `custom`.
6. `canonical.id`, aliases, and `canonical.src` must not exceed 100 characters.
7. `canonical.id` must not contain `# $ % = [ ] ? < > : / \ | *` or spaces.
8. `canonical.id` must not be empty.
9. `aliases` must not be empty.
10. Alias lists must not be empty, except for `custom`.
11. `canonical.src` must not be empty.
12. The `rejected` field must exist.
13. An entry must not appear in both `aliases` and `rejected`.
14. Alias versions must match the canonical version where version matching applies.
15. `isMajorVersionOnly` must match the canonical versioning pattern.

## Organization Checks

These checks apply to data under `data/orgs/`:

1. Organization folder names must be unique.
2. Organization folder names must not use reserved names like `stableMap` or `riskyMap`.
3. Every file inside an organization folder must use that organization name as `canonical.src`.
4. No canonical identifier or alias may overlap between OSS data and organization data.

## Why This Exists

These checks catch structural problems early. They do not guarantee semantic correctness, which is why rejected entries and risky mappings still exist.

## Related Pages

- [Data Specification](data-specification.md)
- [Adding Mappings](../contributing/adding-mappings.md)
- [Organization Mappings](../contributing/organization-mappings.md)
