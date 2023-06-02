| | | |
|---:|:---:|:---:|
| [**main**](https://github.com/pmonks/lice-comb/tree/main) | [![CI](https://github.com/pmonks/lice-comb/workflows/CI/badge.svg?branch=main)](https://github.com/pmonks/lice-comb/actions?query=workflow%3ACI+branch%3Amain) | [![Dependencies](https://github.com/pmonks/lice-comb/workflows/dependencies/badge.svg?branch=main)](https://github.com/pmonks/lice-comb/actions?query=workflow%3Adependencies+branch%3Amain) |
| [**dev**](https://github.com/pmonks/lice-comb/tree/dev) | [![CI](https://github.com/pmonks/lice-comb/workflows/CI/badge.svg?branch=dev)](https://github.com/pmonks/lice-comb/actions?query=workflow%3ACI+branch%3Adev) | [![Dependencies](https://github.com/pmonks/lice-comb/workflows/dependencies/badge.svg?branch=dev)](https://github.com/pmonks/lice-comb/actions?query=workflow%3Adependencies+branch%3Adev) |

[![Latest Version](https://img.shields.io/clojars/v/com.github.pmonks/lice-comb)](https://clojars.org/com.github.pmonks/lice-comb/) [![Open Issues](https://img.shields.io/github/issues/pmonks/lice-comb.svg)](https://github.com/pmonks/lice-comb/issues) [![License](https://img.shields.io/github/license/pmonks/lice-comb.svg)](https://github.com/pmonks/lice-comb/blob/main/LICENSE)

<img alt="lice-comb logo: a fine-toothed metal comb for removing headlice emblazoned with the OSI keyhole logo" align="right" width="25%" src="https://raw.githubusercontent.com/pmonks/lice-comb/main/lice-comb-logo.png">

# lice-comb

A Clojure library for software license detection.  It does this by combing through `tools.deps` dependency maps, Maven POMs, directory structures & ZIP files, and attempting to detect what license(s) they contain.

This library leverages, and is inspired by, the *excellent* [SPDX project](https://spdx.dev/).  It's a great shame that it doesn't have greater traction in the Java & Clojure (and wider open source) communities.  If you're new to SPDX and would prefer to read a primer rather than dry specification documents, I can thoroughly recommend [David A. Wheeler's SPDX Tutorial](https://github.com/david-a-wheeler/spdx-tutorial#spdx-tutorial).

## Using the library

### Documentation

[API documentation is available here](https://pmonks.github.io/lice-comb/).

[An FAQ is available here](https://github.com/pmonks/lice-comb/wiki/FAQ).

### Dependency

Express the correct maven dependencies in your `deps.edn`:

```edn
{:deps {com.github.pmonks/lice-comb {:mvn/version "LATEST_CLOJARS_VERSION"}}}
```

### Require one or more of the namespaces

```clojure
(ns your.ns
  (:require [lice-comb.deps  :as lcd]
            [lice-comb.files :as lcf]
            [lice-comb.maven :as lcm]
            [lice-comb.spdx  :as lcs]))
```

## Upgrading

### 1.x -> 2.0

Implementing [issue #3](https://github.com/pmonks/lice-comb/issues/3) resulted in the creation of a [new SPDX-specific library (`clj-spdx`)](https://github.com/pmonks/clj-spdx) that leverages [the official SPDX Java library](https://github.com/spdx/Spdx-Java-Library).  Because of irreconcilable differences in how that Java library represents license data compared to `lice-comb` v1.x, as well as the addition of support for SPDX license exceptions, it was not possible to retain backwards compatibility.

The backwards compatibility breaking changes are limited to the `lice-comb.spdx` namespace however, so if you're not using that namespace you should be unaffected.  If you are using that namespace, migration involves migrating to [`clj-spdx`](https://github.com/pmonks/clj-spdx).  It offers all of the same functionality (and more) as the `lice-comb` v1.x functionality, and by virtue of using the official SPDX Java library is far more battle tested than that code was.

## Contributor Information

[Contributor FAQ](https://github.com/pmonks/lice-comb/wiki/FAQ#contributor-faqs)

[Contributing Guidelines](https://github.com/pmonks/lice-comb/blob/main/.github/CONTRIBUTING.md)

[Bug Tracker](https://github.com/pmonks/lice-comb/issues)

[Code of Conduct](https://github.com/pmonks/lice-comb/blob/main/.github/CODE_OF_CONDUCT.md)

### Developer Workflow

This project uses the [git-flow branching strategy](https://nvie.com/posts/a-successful-git-branching-model/), with the caveat that the permanent branches are called `main` and `dev`, and any changes to the `main` branch are considered a release and auto-deployed (JARs to Clojars, API docs to GitHub Pages, etc.).

For this reason, **all development must occur either in branch `dev`, or (preferably) in temporary branches off of `dev`.**  All PRs from forked repos must also be submitted against `dev`; the `main` branch is **only** updated from `dev` via PRs created by the core development team.  All other changes submitted to `main` will be rejected.

### Build Tasks

`lice-comb` uses [`tools.build`](https://clojure.org/guides/tools_build). You can get a list of available tasks by running:

```
clojure -A:deps -T:build help/doc
```

Of particular interest are:

* `clojure -T:build test` - run the unit tests
* `clojure -T:build lint` - run the linters (clj-kondo and eastwood)
* `clojure -T:build ci` - run the full CI suite (check for outdated dependencies, run the unit tests, run the linters)
* `clojure -T:build install` - build the JAR and install it locally (e.g. so you can test it with downstream code)

Please note that the `deploy` task is restricted to the core development team (and will not function if you run it yourself).

## License

Copyright © 2021 Peter Monks

Distributed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

SPDX-License-Identifier: [Apache-2.0](https://spdx.org/licenses/Apache-2.0)

The OSI "Keyhole Logo" is used as per the [Open Source Initiative's](https://opensource.org/) [trademark](https://opensource.org/trademark-guidelines) and [logo usage](https://opensource.org/logo-usage-guidelines) policies.
