| | | |
|---:|:---:|:---:|
| [**release**](https://github.com/pmonks/lice-comb/tree/release) | [![CI](https://github.com/pmonks/lice-comb/actions/workflows/ci.yml/badge.svg?branch=release)](https://github.com/pmonks/lice-comb/actions?query=workflow%3ACI+branch%3Arelease) | [![Dependencies](https://github.com/pmonks/lice-comb/actions/workflows/dependencies.yml/badge.svg?branch=release)](https://github.com/pmonks/lice-comb/actions?query=workflow%3Adependencies+branch%3Arelease) |
| [**dev**](https://github.com/pmonks/lice-comb/tree/dev) | [![CI](https://github.com/pmonks/lice-comb/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/pmonks/lice-comb/actions?query=workflow%3ACI+branch%3Adev) | [![Dependencies](https://github.com/pmonks/lice-comb/actions/workflows/dependencies.yml/badge.svg?branch=dev)](https://github.com/pmonks/lice-comb/actions?query=workflow%3Adependencies+branch%3Adev) |

[![Latest Version](https://img.shields.io/clojars/v/com.github.pmonks/lice-comb)](https://clojars.org/com.github.pmonks/lice-comb/) [![License](https://img.shields.io/github/license/pmonks/lice-comb.svg)](https://github.com/pmonks/lice-comb/blob/release/LICENSE) [![Open Issues](https://img.shields.io/github/issues/pmonks/lice-comb.svg)](https://github.com/pmonks/lice-comb/issues) [![Vulnerabilities](https://github.com/pmonks/lice-comb/actions/workflows/vulnerabilities.yml/badge.svg)](https://pmonks.github.io/lice-comb/nvd/dependency-check-report.html)

<img alt="lice-comb logo: a fine-toothed metal comb for removing headlice emblazoned with the OSI keyhole logo" align="right" width="25%" src="https://raw.githubusercontent.com/pmonks/lice-comb/release/lice-comb-logo.png">

# lice-comb

A Clojure library for software *lice*nse detection.  It does this by *comb*ing through tools.deps and Leiningen dependencies (i.e. artifacts hosted on Maven repositories), directory structures, and JAR & ZIP files, attempting to detect what license(s) they reference and/or contain, and then normalising them into [SPDX license expressions](https://spdx.github.io/spdx-spec/v2.3/SPDX-license-expressions/).

This library leverages, and is inspired by, the *excellent* [SPDX project](https://spdx.dev/).  It's a great shame that it doesn't have greater traction in the Java & Clojure (and wider open source) communities.  If you're new to SPDX and would prefer to read a primer rather than dry specification documents, [David A. Wheeler's SPDX Tutorial](https://github.com/david-a-wheeler/spdx-tutorial#spdx-tutorial) is a good (albeit slightly outdated) intro.

## Disclaimer

**The author and contributors to `lice-comb` are not lawyers, and neither they nor `lice-comb` itself provides legal advice. This is nothing more than logic to assist in finding license information.**  If you need a primer on the legal aspects of open source software, the author has found the [Blue Oak Council](https://blueoakcouncil.org/) to be a useful resource.

## System Requirements

* `lice-comb` (v2.0+) requires JDK 11 or higher.

* `lice-comb` (all versions) requires an internet connection.

* `lice-comb` (all versions) assumes Maven is installed and in the `PATH` (but has fallback logic if it isn't available).

## Installation

`lice-comb` is available as a Maven artifact from [Clojars](https://clojars.org/com.github.pmonks/lice-comb).

### Trying it Out

#### Clojure CLI

```shell
$ clj -Sdeps '{:deps {com.github.pmonks/lice-comb {:mvn/version "RELEASE"}}}'
```

#### Leiningen

```shell
$ lein try com.github.pmonks/lice-comb
```

#### deps-try

```shell
$ deps-try com.github.pmonks/lice-comb
```

### Demo

```clojure
;; Core matching functionality
(require '[lice-comb.matching :as lcm])

; Initialise the matching namespace
; Notes:
; 1. This is slow the first time it's run, due to Spdx-Java-Library downloading SPDX files
;    from the internet and caching them (it takes ~1 minute on my laptop). It's substantially
;    faster on subsequent invocations however.
; 2. This step is optional, though initialisation will still happen regardless, and when it
;    does you'll incur the same cost
(lcm/init!)

(lcm/name->expressions "Apache")
;=> #{"Apache-2.0"}

(lcm/name->expressions "GNU Public License 2.0 w/ the GNU Classpath Exception")
;=> #{"GPL-2.0-only WITH Classpath-exception-2.0"}

(lcm/uri->expressions "https://www.apache.org/licenses/LICENSE-2.0.txt")
;=> #{"Apache-2.0"}

(lcm/text->expressions (slurp "https://www.apache.org/licenses/LICENSE-2.0.txt"))
;=> #{"Apache-2.0"}


;; License extraction from Maven GAVs and POMs, including ones that aren't locally downloaded
(require '[lice-comb.maven :as lcmvn])

(lcmvn/gav->expressions "commons-io" "commons-io" "2.15.0")
;=> #{"Apache-2.0"}

; Note: this looks up and uses the latest version of the given project (1.5.0-b01 at the time of
; writing), so the results you get may be different to what you see here
(lcmvn/gav->expressions "javax.mail" "mail")
;=> #{"CDDL-1.1 OR GPL-2.0-only WITH Classpath-exception-2.0"}

(lcmvn/pom->expressions (str (System/getProperty "user.home") "/.m2/repository/org/clojure/clojure/1.11.2/clojure-1.11.2.pom"))
;=> #{"EPL-1.0"}

(lcmvn/pom->expressions "https://repo1.maven.org/maven2/org/springframework/spring-core/6.0.11/spring-core-6.0.11.pom")
;=> #{"Apache-2.0"}


;; License extraction from tools.deps dependency maps
(require '[lice-comb.deps :as lcd])

(lcd/dep->expressions ['org.clojure/clojure {:deps/manifest :mvn :mvn/version "1.12.0-alpha5"}])
;=> #{"EPL-1.0"}


;; License extraction from Leiningen dependency vectors
(require '[lice-comb.lein :as lcl])

(lcl/dep->expressions ['aopalliance/aopalliance "1.0"])
;=> #{"LicenseRef-lice-comb-PUBLIC-DOMAIN"}
; Also shows how lice-comb handles "public domain" attestations (which are not supported
; directly by SPDX, since "public domain" is not a license)


;; Information about matches (useful for better understanding how lice-comb arrived at a given
;; set of expressions, and how confident it is in the values it's providing)
(lcm/name->expressions-info "Apache-2.0")
;=> {"Apache-2.0" ({:type :declared, :strategy :spdx-expression, :source ("Apache-2.0")})}

(lcm/name->expressions-info "GNU Public License 2.0 or later w/ the GNU Classpath Exception")
;=> {"GPL-2.0-or-later WITH Classpath-exception-2.0"
;     ({:type :concluded, :confidence :low, :strategy :expression-inference,
;       :source ("GNU Public License 2.0 or later w/ the GNU Classpath Exception")}
;      {:id "GPL-2.0-or-later", :type :concluded, :confidence :high, :strategy :regex-matching,
;       :source ("GNU Public License 2.0 or later w/ the GNU Classpath Exception"
;                "GNU Public License 2.0 or later")}
;      {:id "Classpath-exception-2.0", :type :concluded, :confidence :low, :strategy :regex-matching,
;       :source ("GNU Public License 2.0 or later w/ the GNU Classpath Exception"
;                "the GNU Classpath Exception"
;                "Classpath Exception"),
;       :confidence-explanations #{:missing-version}})}

(lcmvn/pom->expressions-info "https://repo.clojars.org/canvas/canvas/0.1.6/canvas-0.1.6.pom")
;=> {"EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0"
;     ({:type :declared, :strategy :spdx-expression,
;       :source ("https://repo.clojars.org/canvas/canvas/0.1.6/canvas-0.1.6.pom"
;                "<licenses><license><name>"
;                "EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0")})}


;; Pretty print expressions-info
(require '[lice-comb.utils :as lcu])

(println (lcu/expressions-info->string (lcmvn/gav->expressions-info "com.amazonaws" "aws-java-sdk-s3" "1.12.129")))
;=> Apache-2.0:
;     Concluded
;       Confidence: high
;       Strategy: regular expression matching
;       Source:
;       > com.amazonaws/aws-java-sdk-s3@1.12.129
;       > https://repo.maven.apache.org/maven2/com/amazonaws/aws-java-sdk-s3/1.12.129/aws-java-sdk-s3-1.12.129.pom
;       > https://repo.maven.apache.org/maven2/com/amazonaws/aws-java-sdk-pom/1.12.129/aws-java-sdk-pom-1.12.129.pom
;       > <licenses><license><name>
;       > Apache License, Version 2.0
```

### API Documentation

[API documentation is available here](https://pmonks.github.io/lice-comb/), or [here on cljdoc](https://cljdoc.org/d/com.github.pmonks/lice-comb/).

[An FAQ is available here](https://github.com/pmonks/lice-comb/wiki/FAQ).

## Upgrading

### 1.x -> 2.x

The implementation of [issue #3](https://github.com/pmonks/lice-comb/issues/3) resulted in a number of unavoidable breaking changes, including:

* A wholesale change from returning sets of SPDX identifiers to returning sets of SPDX expressions
* The creation of [a dedicated SPDX-specific library (`clj-spdx`)](https://github.com/pmonks/clj-spdx) that leverages [the official SPDX Java library](https://github.com/spdx/Spdx-Java-Library)

## Contributor Information

[Contributor FAQ](https://github.com/pmonks/lice-comb/wiki/FAQ#contributor-faqs)

[Contributing Guidelines](https://github.com/pmonks/lice-comb/blob/release/.github/CONTRIBUTING.md)

[Bug Tracker](https://github.com/pmonks/lice-comb/issues)

[Code of Conduct](https://github.com/pmonks/lice-comb/blob/release/.github/CODE_OF_CONDUCT.md)

### Developer Workflow

This project uses the [git-flow branching strategy](https://nvie.com/posts/a-successful-git-branching-model/), and the permanent branches are called `release` and `dev`.  Any changes to the `release` branch are considered a release and auto-deployed (JARs to Clojars, API docs to GitHub Pages, etc.).

For this reason, **all development must occur either in branch `dev`, or (preferably) in temporary branches off of `dev`.**  All PRs from forked repos must also be submitted against `dev`; the `release` branch is **only** updated from `dev` via PRs created by the core development team.  All other changes submitted to `release` will be rejected.

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
