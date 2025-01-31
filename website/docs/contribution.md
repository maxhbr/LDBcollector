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
The different programming libraries are separately tagged and released using the following format:

```bash
python_v0.1.0
java_v0.1.0
typescript_v0.1.0
```

The X.Y.Z versioning typically follows this pattern:

**X: Major Versions:**

- Breaks compatibility with the API

**Y: Minor Versions:**

- Introduces new features  
- Makes minor backwards-compatible API changes  

**Z: Hotfix Versions:**

- Critical bug fixes or minor changes
