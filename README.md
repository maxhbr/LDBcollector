# ORT Config

This repository contains configuration files for the [OSS Review Toolkit](https://github.com/oss-review-toolkit/ort).

## Content

### Curations

The [curations](./curations/) directory contains
[package curations](https://github.com/oss-review-toolkit/ort/blob/main/docs/config-file-curations-yml.md) for
open source packages.

Package curations submitted to this repository must adhere to the following rules:

* Declaring authors, declared licenses, and concluded licenses is currently not allowed.
* Curations that apply to whole namespaces by only setting the type and namespace of the identifier are not allowed.
* The curation file path must be `curations/[type]/[namespace]/[name].yml`. If the namespace is empty, use "_". For
  example a curation for the package `NuGet::Azure.Core:1.2.0` must be in the file `curation/NuGet/_/Azure.Core.yml`.

Package configurations containing license finding curations or path excludes are not yet supported.

### Tools

The [tools](./tools/) directory contains tools that help generating curations.

## Usage

To use the configuration provided by this repository, it needs to be cloned, and the files need to be passed to the
respective options of the ORT CLI commands. For example, to use the curations with the ORT analyzer:

```
ort analyze --package-curations-dir [path-to-curations-dir]
```

Using this repository together with ORT will be simplified in future.

## Contribute

This repository is currently in incubation and not yet ready for contributions.

# License

Copyright (C) 2022 Bosch.IO GmbH

See the [LICENSE](./LICENSE) file in the root of this project for license details.

OSS Review Toolkit (ORT) is a [Linux Foundation project](https://www.linuxfoundation.org) and part of
[ACT](https://automatecompliance.org/).
