# Contributing

## Developing Code

The project is a monorepo with five different subprojects.  
The ``scripts`` folder is a Python project where the data is updated, loaded, and validated.

The folders ``Python``, ``TypeScript``, and ``Java`` contain the implementation of the data mappings, written in the programming languages corresponding to their folder names.

The folder ``website`` is an MkDocs project using Material as the theme.  
This folder is published via GitLab Pages.

Including new data sources or new libraries for programming languages can be done via a merge request.  
It is important that unit tests are also implemented with a coverage of at least 90%.

## Reporting Issues

If you detect a bug in the software or find an error in the data, simply create an issue to report it.  
For feature requests, create a new issue if one does not already exist.

## Releases

LicenseLynx uses [semantic versioning](https://semver.org).  
The different programming libraries are tagged with the same version:

```bash
v0.1.0
```

The X.Y.Z versioning typically follows this pattern:

**X: Major Versions:**

- Breaks compatibility with the API

**Y: Minor Versions:**

- Introduces new features  
- Makes minor backwards-compatible API changes  

**Z: Hotfix Versions:**

- Critical bug fixes or minor changes

The reason why we use only one tag is to simplify our release cycle because most changes between versions will be data updates.
These updates are treated as patch-level changes because the data is not part of the library's core API.
Although the data is bundled with the library as a json file, applications should not depend on it.

If non-data update is made, then all libraries will get the version bump, even if nothing changed for certain library.
The release notes will clarify, what changed for which library if the update is more than a data update.
