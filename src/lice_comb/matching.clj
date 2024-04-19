;
; Copyright © 2021 Peter Monks
;
; Licensed under the Apache License, Version 2.0 (the "License");
; you may not use this file except in compliance with the License.
; You may obtain a copy of the License at
;
;     http://www.apache.org/licenses/LICENSE-2.0
;
; Unless required by applicable law or agreed to in writing, software
; distributed under the License is distributed on an "AS IS" BASIS,
; WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
; See the License for the specific language governing permissions and
; limitations under the License.
;
; SPDX-License-Identifier: Apache-2.0
;

(ns lice-comb.matching
  "The core matching functionality within lice-comb. Matching is provided for
  three categories of input, and uses a different process for each:

  1. License names
  2. License uris
  3. License texts

  Each matching fn has two variants:

  1. A 'simple' version that returns a set of SPDX expressions (`String`s)
  2. An 'info' version that returns an 'expressions-info map' containing
     metadata on how the determination was made (including confidence
     information)

  An expressions-info map has this structure:
  
  * key:   an SPDX expression (`String`)
  * value: a sequence of 'expression-info' maps

  An expression-info map has this structure:
  
  * `:id` (`String`, optional):
    The portion of the SPDX expression that this info map refers to (usually,
    though not always, a single SPDX identifier).
  * `:type` (either `:declared` or `:concluded`, mandatory):
    Whether this identifier was unambiguously declared within the input or was
    instead concluded by lice-comb (see [the SPDX FAQ](https://wiki.spdx.org/view/SPDX_FAQ)
    for more detail on the definition of these two terms).
  * `:confidence` (one of: `:high`, `:medium`, `:low`, only provided when
    `:type` = `:concluded`):
    Indicates the approximate confidence lice-comb has in its conclusions for
    this particular SPDX identifier.
  * `:strategy` (a keyword, mandatory):
    The strategy lice-comb used to determine this particular SPDX identifier.
    See [[lice-comb.utils/strategy->string]] for an up-to-date list of all
    possible values.
  * `:source` (a sequence of `String`s):
    The list of sources used to arrive at this portion of the SPDX expression,
    starting from the most general (the input) through to the most specific
    (the smallest subset of the input that was used to make this
    determination)."
  (:require [clojure.string          :as s]
            [spdx.licenses           :as sl]
            [spdx.exceptions         :as se]
            [spdx.expressions        :as sexp]
            [lice-comb.impl.spdx     :as lcis]
            [lice-comb.impl.matching :as lcim]
            [lice-comb.impl.utils    :as lciu]))

(defn lice-comb-license-ref?
  "Is the given id one of lice-comb's custom LicenseRefs?"
  [id]
  (lcis/lice-comb-license-ref? id))

(defn public-domain?
  "Is the given id lice-comb's custom 'public domain' LicenseRef?"
  [id]
  (lcis/public-domain? id))

(defn proprietary-commercial?
  "Is the given id lice-comb's custom 'proprietary / commercial' LicenseRef?"
  [id]
  (lcis/proprietary-commercial? id))

(defn unidentified?
  "Is the given id a lice-comb custom 'unidentified' LicenseRef?"
  [id]
  (lcis/unidentified? id))

(defn unidentified->name
  "Returns a human readable name for the given lice-comb custom 'unidentified'
  LicenseRef. Returns `nil` if id is not a lice-comb custom 'unidentified'
  LicenseRef."
  [id]
  (lcis/unidentified->human-readable-name id))

(defn id->name
  "Returns a human readable name of the given license or exception identifier;
  either the official SPDX license or exception name or, if the id is a
  lice-comb specific LicenseRef, a lice-comb specific name. Returns `id`
  verbatim if unable to determine a name. Returns `nil` if `id` is blank."
  [id]
  (when-not (s/blank? id)
    (cond (sl/listed-id? id)           (:name (sl/id->info id))
          (se/listed-id? id)           (:name (se/id->info id))
          (public-domain? id)          "Public domain"
          (proprietary-commercial? id) "Proprietary/commercial"
          (unidentified? id)           (unidentified->name id)
          :else                        id)))

(defn text->expressions-info
  "Returns an expressions-info map for `text` (a `String`, `Reader`, or anything
  that's accepted by `clojure.java.io/reader`). Returns `nil` if no expressions
  were found in it.

  Notes:

  * this function implements the SPDX matching guidelines (via clj-spdx).
    See [the SPDX specification](https://spdx.github.io/spdx-spec/v2.3/license-matching-guidelines-and-templates/)
    for details
  * the caller is expected to open & close a `Reader` or `InputStream` passed to
    this function (e.g. using `clojure.core/with-open`)
  * you cannot pass a `String` representation of a filename to this method - you
    should pass filenames through `clojure.java.io/file` (or similar) first"
  [text]
  (lcim/text->expressions-info text))

(defn text->expressions
  "Returns a set of SPDX expressions (`String`s) for `text`. See
  [[text->expressions-info]] for details."
  [text]
  (some-> (text->expressions-info text)
          keys
          set))

(defn uri->expressions-info
  "Returns an exceptions-info map for `uri` (a `String`, `URL`, or `URI`), or
  `nil` if no expressions were found.  It does this via two steps:

  1. Seeing if `uri` is in the SPDX license and/or exception lists
  2. Attempting to retrieve the plain text content of `uri` and if that succeeds
     running that text through [[text->expressions-info]]

  Notes on step 1:

  1. this does not perform exact matching; rather it simplifies URIs in various
     ways to avoid irrelevant differences, including performing a
     case-insensitive comparison, ignoring protocol differences (http vs https),
     ignoring extensions representing MIME types (.txt vs .html, etc.), etc.
  2. URIs in the SPDX license and exception lists are not unique - the same URI
     may represent multiple licenses and/or exceptions."
  [uri]
  (lcim/uri->expressions-info uri))

(defn uri->expressions
  "Returns a set of SPDX expressions (`String`s) for `uri`. See
  [[uri->expressions-info]] for details."
  [uri]
  (some-> (uri->expressions-info uri)
          keys
          set))

(defn name->expressions-info
  "Returns an expressions-info map for `name` (a `String`), or `nil` if no
  expressions were found.  This involves:

  1. Determining whether `name` is a valid SPDX license expression, and if so
     normalising it (see [clj-spdx's `spdx.expressions/normalise` fn](https://pmonks.github.io/clj-spdx/spdx.expressions.html#var-normalise))
  2. Checking if `name` is actually a URI, and if so performing URL matching
     on it via [[uri->expressions-info]]
  3. attempting to parse `name` to construct one or more SPDX license
     expressions"
  [name]
  (when-not (s/blank? name)
    (let [name (s/trim name)]
      ; 1. If it's a valid SPDX expression, return the normalised rendition of it
      (if-let [normalised-expression (sexp/normalise name)]
        {normalised-expression (list {:type :declared :strategy :spdx-expression :source (list name)})}
        ; 2. If it's a URI, use URI matching (this is to handle messed up real world cases where license names in POMs contain a URI)
        (if (lciu/valid-http-uri? name)
          (if-let [ids (uri->expressions-info name)]
            ids
            {(lcis/name->unidentified name) (list {:type :concluded :confidence :low :strategy :unidentified :source (list name)})})  ; It was a URL, but we weren't able to resolve it to any ids, so return it as unidentified
          ; 3. Attempt to build SPDX expression(s) from the name
          (lcim/name->expressions-info name))))))

(defn name->expressions
  "Returns a set of SPDX expressions (`String`s) for `name`. See
  [[name->expressions-info]] for details."
  [name]
  (some-> (name->expressions-info name)
          keys
          set))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning `nil`. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it.

  Note: this method may have a substantial performance cost."
  []
  (lcis/init!)
  (lcim/init!)
  nil)
