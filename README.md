# ORT Config

This repository contains configuration files for the [OSS Review Toolkit](https://github.com/oss-review-toolkit/ort).

## Content

### Curations

The [curations](./curations/) directory contains
[package curations](https://github.com/oss-review-toolkit/ort/blob/master/docs/config-file-curations-yml.md) for
open source packages. At this time, only technical curations are allowed, for example adding missing VCS information.
Curations for legally relevant properties like licenses or authors are forbidden.

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
