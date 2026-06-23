# New Language Library

If you want to add a new LicenseLynx library, start from one of the existing implementations and match its public behavior.

## Open an Issue First

Before starting implementation, first open an issue so the new library can be discussed.

This keeps the scope aligned early and avoids building a library that does not match the intended direction of the project.

Read these pages first:

- [API Reference](../api-reference.md)
- [Matching Behavior](../data/matching-behavior.md)
- [How LicenseLynx works](../licenselynxworks.md)

## What a Library Needs to Do

A new library should:

- load the merged mapping data
- expose a `map()` function or method
- support stable lookups, risky lookups, and organization-specific lookups
- apply the same quote normalization as the existing libraries
- return the canonical identifier and source
- include tests

The public behavior should match the docs, even if the internal implementation is different.

## Where to Start

Use one of the existing libraries as your reference:

- `python/`
- `java/`
- `typescript/`

## Typical Repo Changes

A new language contribution usually needs:

1. A new top-level folder for the library.
2. Build or package metadata for that ecosystem.
3. A way to load `merged_data.json`.
4. Unit tests and smoke tests.
5. A CI workflow under `.github/workflows/`.

## Documentation Updates

When the new library is ready, update:

- [Installation](../installation.md)
- [Usage](../usage.md)
- [API Reference](../api-reference.md)

## Suggested Order

For a first implementation, this order is usually easiest:

1. Get one stable lookup working.
2. Add risky lookup support.
3. Add organization-specific lookup support.
4. Add quote normalization.
5. Add tests.
6. Add packaging and CI.
7. Update the docs.

## Minimum Test Cases

Before opening a pull request, the new library should cover at least:

- a normal stable lookup
- a no-match case
- a risky lookup
- an organization-specific lookup
- a quote-normalization lookup

## For New Contributors

Keep the first version small.

Do not try to solve packaging, publishing, CI, and every helper function at once. First make the core lookup work and align it with the documented behavior. After that, fill in the surrounding pieces.
