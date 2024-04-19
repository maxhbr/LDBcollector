# Overview

Most of the namespaces in this library provide two variants of every license detection function:

  1. A 'simple' version that returns a set of SPDX expressions (`String`s)
  2. An 'info' version that returns an 'expressions-info map' containing metadata on how the determination was made (including confidence & source information)

If all you're interested in are the license expressions themselves, the 'simple' variant is what you're after (e.g. [[lice-comb.matching/name->expressions]]).  However in choosing to use these 'simple' variants you're placing full faith & confidence that lice-comb has done the right thing.  Given that license matching is a messy business, you may wish to have better visibility into how lice-comb made a particular determination, and that can be done with the 'info' variants (e.g. [[lice-comb.matching/name->expressions-info]]).

## expressions-info map

The 'info' variants all return an 'expressions-info' map, which has this structure:
  
  * key:   an SPDX expression (`String`)
  * value: a sequence of 'expression-info' maps

## expression-info map

Each expression-info map in the sequence of values has this structure:
  
  * `:id` (`String`, optional):
    The portion of the SPDX expression that this info map refers to (usually, though not always, a single SPDX identifier).
  * `:type` (either `:declared` or `:concluded`, mandatory):
    Whether this identifier was unambiguously declared within the input or was instead concluded by lice-comb (see [the SPDX FAQ](https://wiki.spdx.org/view/SPDX_FAQ) for more detail on the definition of these two terms).
  * `:confidence` (one of: `:high`, `:medium`, `:low`, only provided when `:type` = `:concluded`):
    Indicates the approximate confidence lice-comb has in its conclusions for this particular SPDX identifier.
  * `:strategy` (a keyword, mandatory):
    The strategy lice-comb used to determine this particular SPDX identifier.  See [[lice-comb.utils/strategy->string]] for an up-to-date list of all possible values.
  * `:source` (a sequence of `String`s):
    The list of sources used to arrive at this portion of the SPDX expression, starting from the most general (the input) through to the most specific (the smallest subset of the input that was used to make this determination.  These may include dependencies expressed in Leiningen or tools.deps format, Maven GAVs, file paths, URIs, XML tags, text fragments, and other string data, and are intended for human, rather than programmatic, consumption.

## Example

For example, this code:

```clojure
(require '[lice-comb.maven :as lcmvn])
(lcmvn/gav->expressions-info "javax.mail" "javax.mail-api" "1.6.2")
```

results in this expressions-info map (pretty printed for clarity):

```clojure
{"GPL-2.0-or-later"
   ({:id         "GPL-2.0-or-later",
     :type       :concluded,
     :confidence :medium,
     :strategy   :regex-matching,
     :source     ("https://repo1.maven.org/maven2/javax/mail/javax.mail-api/1.6.2/javax.mail-api-1.6.2.pom"
                  "https://repo1.maven.org/maven2/com/sun/mail/all/1.6.2/all-1.6.2.pom"
                  "<licenses><license><name>"
                  "CDDL/GPLv2+CE"
                  "GPLv2+")}),
 "CDDL-1.1"
   ({:id         "CDDL-1.1",
     :type       :concluded,
     :confidence :low,
     :strategy   :regex-matching,
     :source     ("https://repo1.maven.org/maven2/javax/mail/javax.mail-api/1.6.2/javax.mail-api-1.6.2.pom"
                  "https://repo1.maven.org/maven2/com/sun/mail/all/1.6.2/all-1.6.2.pom"
                  "<licenses><license><name>"
                  "CDDL/GPLv2+CE"
                  "CDDL")})}
```

A key insight that the expressions-info map tells us in this case is that the `javax.mail/javax.mail-api@1.6.2` artifact doesn't declare which version of the CDDL it uses, and lice-comb has _inferred_ the latest (`CDDL-1.1`), and in doing so reduced its confidence to "low".  This important insight is not apparent when the `simple` variant of the function is used instead:

```clojure
(lcmvn/gav->expressions "javax.mail" "javax.mail-api" "1.6.2")

#{"CDDL-1.1" "GPL-2.0-or-later"}
```

[Back to GitHub](https://github.com/pmonks/lice-comb)