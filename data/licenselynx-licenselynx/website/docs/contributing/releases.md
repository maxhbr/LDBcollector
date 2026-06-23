# Releases

LicenseLynx uses [semantic versioning](https://semver.org).

All libraries are tagged with the same version:

```bash
v0.1.0
```

## Versioning

- **X**: breaking API changes
- **Y**: new features or small backwards-compatible API changes
- **Z**: hotfixes and minor changes

## Why There Is Only One Tag

LicenseLynx uses one shared version to keep releases simple across the three libraries.
Most changes between versions are data updates, so releasing all libraries together keeps the bundled data aligned.

## Data Updates

Data-only changes are treated as patch-level changes because the mapping data is not part of the public API contract, even though it is shipped with the libraries.

## Non-Data Updates

If a code change affects only one library, all libraries still receive the same version bump.
The release notes should clarify which library actually changed.
