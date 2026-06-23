# Organization Mappings

Organization mappings are stored separately from OSS mappings under `data/orgs/`.

## Folder Layout

Each organization gets its own folder:

```text
data/
  orgs/
    siemens/
      SISL-1.4.json
      SISL-1.5.json
```

Each file uses the same JSON structure as an OSS mapping.

## Rules

1. Put the file into `data/orgs/<org>/`.
2. Set `canonical.src` to the organization name.
   For files in `data/orgs/siemens/`, the source must be `siemens`.
3. Do not use reserved organization names.
   `stableMap` and `riskyMap` are reserved.
4. Do not overlap with OSS data.
   Organization identifiers and aliases must not collide with identifiers or aliases from `data/`.
5. Keep the same file rules as OSS mappings.
   Filename, alias keys, rejected handling, risky handling, and version checks still apply.

## What Is Allowed

- Different organizations may reuse the same identifiers or aliases.
- Organization mappings are loaded into their own top-level map in `merged_data.json`.
- All libraries can query organization mappings through the optional `org` parameter.

## Adding a New Organization

Adding files under `data/orgs/<org>/` is only one part of the change. A new organization must also be added to the `Organization` enum in each library so it can be selected through the public API.
