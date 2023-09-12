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
  1. A 'simple' version that returns a set of SPDX expressions (Strings)
  2. An 'info' version that returns an 'expressions-info map'

  An expressions-info map has this structure:
  * key:   an SPDX expression (String), which may be a single SPDX license
           identifier)
  * value: a sequence of 'expression-info' maps

  Each lice-comb expression-info map has this structure:
  * :id (String, optional):
    The SPDX identifier within the expression that this info map refers to.
  * :type (either :declared or :concluded, mandatory):
    Whether this identifier was unambiguously declared within the input or
    was instead concluded by lice-comb (see SPDX specification for more detail
    on the definition of these two terms).
  * :confidence (one of: :high, :medium, :low, only provided when :type = :concluded):
    Indicates the approximate confidence lice-comb has in its conclusions for
    this particular SPDX identifier.
  * :strategy (a keyword, mandatory):
    The strategy lice-comb used to determine this particular SPDX identifier.
    See the source for lice-comb.utils for an up-to-date list of all possible
    values.
  * :source (a sequence of Strings):
    The list of sources used to arrive at this SPDX identifier, starting from
    the most general (the input) to the most specific (the smallest subset of
    the input that was used to make this determination)."
  (:require [clojure.string          :as s]
            [spdx.licenses           :as sl]
            [spdx.exceptions         :as se]
            [spdx.expressions        :as sexp]
            [lice-comb.impl.spdx     :as lcis]
            [lice-comb.impl.matching :as lcim]
            [lice-comb.impl.utils    :as lciu]))

(defn public-domain?
  "Is the given id lice-comb's custom 'public domain' LicenseRef?"
  [id]
  (lcis/public-domain? id))

(defn proprietary-commercial?
  "Is the given id lice-comb's custom 'proprietary / commercial' LicenseRef?"
  [id]
  (lcis/proprietary-commercial? id))

(defn unlisted?
  "Is the given id a lice-comb custom 'unlisted' LicenseRef?"
  [id]
  (lcis/unlisted? id))

(defn id->name
  "Returns the human readable name of the given license or exception identifier;
  either the official SPDX license or exception name or, if the id is a
  lice-comb specific LicenseRef, a lice-comb specific name. Returns the id
  verbatim if unable to determine a name. Returns nil if the id is blank."
  [id]
  (when-not (s/blank? id)
    (cond (sl/listed-id? id)           (:name (sl/id->info id))
          (se/listed-id? id)           (:name (se/id->info id))
          (public-domain? id)          "Public domain"
          (proprietary-commercial? id) "Proprietary/commercial"
          (unlisted? id)               (lcis/unlisted->name id)
          :else                        id)))

(defn text->ids-info
  "Returns an expressions-info map for the given license text (a String, Reader,
  InputStream, or something that is accepted by clojure.java.io/reader - File,
  URL, URI, Socket, etc.), or nil if no expressions were found.

  Notes:
  * this function implements the SPDX matching guidelines (via clj-spdx).
    See https://spdx.github.io/spdx-spec/v2.3/license-matching-guidelines-and-templates/
  * the caller is expected to open & close a Reader or InputStream passed to
    this function (e.g. using clojure.core/with-open)
  * you cannot pass a String representation of a filename to this method - you
    should pass filenames through clojure.java.io/file (or similar) first"
  [text]
  (lcim/text->ids text))

(defn text->ids
  "Returns a set of SPDX expressions (Strings) for the given license text (a
  String, Reader, InputStream, or something that is accepted by
  clojure.java.io/reader - File, URL, URI, Socket, etc.), or nil if no
  expressions were found.

  Notes:
  * this function implements the SPDX matching guidelines (via clj-spdx).
    See https://spdx.github.io/spdx-spec/v2.3/license-matching-guidelines-and-templates/
  * the caller is expected to open & close a Reader or InputStream passed to
    this function (e.g. using clojure.core/with-open)
  * you cannot pass a String representation of a filename to this method - you
    should pass filenames through clojure.java.io/file (or similar) first"
  [text]
  (some-> (text->ids-info text)
          keys
          set))

(defn uri->ids-info
  "Returns an exceptions-info map for the given license uri (a String, URL, or
  URI).

  Notes:
  * This is done



  Returns the SPDX license and/or exception identifiers (a map) for the given
  uri, or nil if there aren't any.  It does this via two steps:
  1. Seeing if the given URI is in the license or exception list, and returning
     the ids of the associated licenses and/or exceptions if so
  2. Attempting to retrieve the plain text content of the given URI and
     performing full SPDX license matching on the result if there was one

  Notes on step 1:
  1. this does not perform exact matching; rather it simplifies URIs in various
     ways to avoid irrelevant differences, including performing a
     case-insensitive comparison, ignoring protocol differences (http vs https),
     ignoring extensions representing MIME types (.txt vs .html, etc.), etc.
     See lice-comb.impl.utils/simplify-uri for exact details.
  2. URIs in the SPDX license and exception lists are not unique - the same URI
     may represent multiple licenses and/or exceptions.

  The keys in the maps are the detected SPDX license and exception identifiers,
  and each value contains information about how that identifiers was determined."
  [uri]
  (lcim/uri->ids uri))

(defn uri->ids
  "Returns the SPDX license and/or exception identifiers (a set of Strings) for
  the given uri, or nil if there aren't any.  It does this via two steps:
  1. Seeing if the given URI is in the license or exception list, and returning
     the ids of the associated licenses and/or exceptions if so
  2. Attempting to retrieve the plain text content of the given URI and
     performing full SPDX license matching on the result if there was one

  Notes on step 1:
  1. this does not perform exact matching; rather it simplifies URIs in various
     ways to avoid irrelevant differences, including performing a
     case-insensitive comparison, ignoring protocol differences (http vs https),
     ignoring extensions representing MIME types (.txt vs .html, etc.), etc.
     See lice-comb.impl.utils/simplify-uri for exact details.
  2. URIs in the SPDX license and exception lists are not unique - the same URI
     may represent multiple licenses and/or exceptions."
  [uri]
  (some-> (uri->ids-info uri)
          keys
          set))

(defn name->expressions-info
  "Returns a lice-comb expressions-info map for the given 'license name' (a
  String), or nil if there isn't one.  This involves:
  1. Determining whether the name is a valid SPDX license expression, and if so
     normalising it (see clj-spdx's spdx.expressions/normalise fn)
  2. Checking if the name is actually a URI, and if so performing URL matching
     on it (as per url->ids-info)
  3. attempting to construct one or more SPDX license expressions from the
     name

  The keys in the maps are the detected SPDX license and exception identifiers,
  and each value contains information about how that identifiers was determined."
  [name]
  (when-not (s/blank? name)
    (let [name (s/trim name)]
      ; 1. If it's a valid SPDX expression, return the normalised rendition of it in a set
      (if-let [normalised-expression (sexp/normalise name)]
        {normalised-expression (list {:type :declared :strategy :spdx-expression :source (list name)})}
        ; 2. If it's a URI, use URI matching (this is to handle messed up real world cases where license names in POMs contain a URI)
        (if (lciu/valid-http-uri? name)
          (if-let [ids (uri->ids-info name)]
            ids
            {(lcis/name->unlisted name) (list {:type :concluded :confidence :low :strategy :unlisted :source (list name)})})  ; It was a URL, but we weren't able to resolve it to any ids, so return it as unlisted
          ; 3. Attempt to build SPDX expression(s) from the name
          (lcim/name->expressions-info name))))))

(defn name->expressions
  "Attempts to determine the SPDX license expression(s) (a set of Strings) from
  the given 'license name' (a String), or nil if there aren't any.  This involves:
  1. Determining whether the name is a valid SPDX license expression, and if so
     normalising (see clj-spdx's spdx.expressions/normalise fn) and returning it
  2. Checking if the name is actually a URI, and if so performing URL matching
     on it (as per url->ids)
  3. attempting to construct one or more SPDX license expressions from the
     name"
  [name]
  (some-> (name->expressions-info name)
          keys
          set))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it.

  Note: this method has a substantial performance cost."
  []
  (lcis/init!)
  (lcim/init!)
  nil)
