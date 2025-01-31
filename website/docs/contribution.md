# Contributing

## Developing Code

The project is a monorepo with five different subprojects.
The ``scripts`` folder is a Python project, where the data is updated, loaded, and validated.

The folders ``Python``, ``TypeScript``, and ``Java`` are the implementation of the data mappings, written in the programming languages of their folder's name.

The folder ``website`` is an mkdocs-project using material as theme.
This folder is published via GitLab Pages.

Including new data sources or new libraries for programming languages can be done via merge request.
Important is that unit tests are also implemented with a coverage of at least 90%.

## Reporting Issues

If you detect a bug in the software or the data has an error, simply create an issue to report it.
Also for feature requests create a new issue if not already exisiting.

## Releases

LicenseLynx uses [semantic versioning](https://semver.org).
The different programming libraries are separatly tagged and released with following format:

```bash
python_v0.1.0
java_v0.1.0
typescript_v0.1.0
```

The X.Y.Z versioning follows typically following pattern:

**X: Major Versions:**

- Breaks compatibility with the API

**Y: Minor Versions:**

- Introduces new features
- Makes minor backwards-compatible API changes

**Z: Hotfix Versions:**

- Critical bug fixes or minor changes
