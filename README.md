| | | |
|---:|:---:|:---:|
| [**main**](https://github.com/pmonks/lice-comb/tree/main) | [![CI](https://github.com/pmonks/lice-comb/workflows/CI/badge.svg?branch=main)](https://github.com/pmonks/lice-comb/actions?query=workflow%3ACI) | [![Dependencies](https://github.com/pmonks/lice-comb/workflows/dependencies/badge.svg?branch=main)](https://github.com/pmonks/lice-comb/actions?query=workflow%3Adependencies) |
| [**dev**](https://github.com/pmonks/lice-comb/tree/dev)  | [![CI](https://github.com/pmonks/lice-comb/workflows/CI/badge.svg?branch=dev)](https://github.com/pmonks/lice-comb/actions?query=workflow%3ACI) | [![Dependencies](https://github.com/pmonks/lice-comb/workflows/dependencies/badge.svg?branch=dev)](https://github.com/pmonks/lice-comb/actions?query=workflow%3Adependencies) |

[![Latest Version](https://img.shields.io/clojars/v/com.github.pmonks/lice-comb)](https://clojars.org/com.github.pmonks/lice-comb/) [![Open Issues](https://img.shields.io/github/issues/pmonks/lice-comb.svg)](https://github.com/pmonks/lice-comb/issues) [![License](https://img.shields.io/github/license/pmonks/lice-comb.svg)](https://github.com/pmonks/lice-comb/blob/main/LICENSE)

<img alt="lice-comb logo: a fine-toothed metal comb for removing headlice emblazoned with the OSI keyhole logo" align="right" width="25%" src="https://raw.githubusercontent.com/pmonks/lice-comb/main/lice-comb-logo.png">

# lice-comb

A Clojure library for software license detection.  It does this by combing through text, files, and even entire directory structures, and attempting to detect what license(s) they contain.

This library leverages, and is inspired by, the *excellent* [SPDX project](https://spdx.dev/).  It's a great shame that it doesn't have greater traction in the Java & Clojure (and wider open source) communities.

## Using the library

### Documentation

[API documentation is available here](https://pmonks.github.io/lice-comb/).

[An FAQ is available here](https://github.com/pmonks/lice-comb/wiki/FAQ).

### Dependency

Express the correct maven dependencies in your `deps.edn`:

```edn
{:deps {com.github.pmonks/lice-comb {:mvn/version "LATEST_CLOJARS_VERSION"}}}
```

### Require the namespace

```clojure
(ns your.ns
  (:require [lice-comb.api :as lic]))
```

## Contributor Information

[Contributing Guidelines](https://github.com/pmonks/lice-comb/blob/main/.github/CONTRIBUTING.md)

[Bug Tracker](https://github.com/pmonks/lice-comb/issues)

[Code of Conduct](https://github.com/pmonks/lice-comb/blob/main/.github/CODE_OF_CONDUCT.md)

### Developer Workflow

The repository has two permanent branches: `main` and `dev`.  **All development must occur either in branch `dev`, or (preferably) in feature branches off of `dev`.**  All PRs must also be submitted against `dev`; the `main` branch is **only** updated from `dev` via PRs created by the core development team.  All other changes submitted to `main` will be rejected.

This model allows otherwise unrelated changes to be batched up in the `dev` branch, integration tested there, and then released en masse to the `main` branch, which will trigger automated generation and deployment of the release (Codox docs to github.io, JARs to Clojars, etc.).

## License

Copyright © 2021 Peter Monks

Distributed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

SPDX-License-Identifier: [Apache-2.0](https://spdx.org/licenses/Apache-2.0)

The OSI "Keyhole Logo" is used as per the [Open Source Initiative's](https://opensource.org/) [trademark](https://opensource.org/trademark-guidelines) and [logo usage](https://opensource.org/logo-usage-guidelines) policies.
