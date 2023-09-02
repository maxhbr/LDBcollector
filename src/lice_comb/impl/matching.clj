;
; Copyright © 2023 Peter Monks
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

(ns lice-comb.impl.matching
  "Matching helper functionality. Note: this namespace is not part of
  the public API of lice-comb and may change without notice."
  (:require [clojure.string                :as s]
            [clojure.set                   :as set]
            [clojure.java.io               :as io]
            [hato.client                   :as hc]
            [spdx.exceptions               :as se]
            [spdx.matching                 :as sm]
            [lice-comb.impl.spdx           :as lcis]
            [lice-comb.impl.regex-matching :as lcirm]
            [lice-comb.impl.3rd-party      :as lc3]
            [lice-comb.impl.utils          :as lcu]))

(def ^:private http-client-d (delay (hc/build-http-client {:connect-timeout 1000
                                                           :redirect-policy :always
                                                           :cookie-policy   :none})))

(def ^:private gpl-ids-with-only-or-later #{"AGPL-1.0"
                                            "AGPL-3.0"
                                            "GFDL-1.1"
                                            "GFDL-1.2"
                                            "GFDL-1.3"
                                            "GPL-1.0"
                                            "GPL-2.0"
                                            "GPL-3.0"
                                            "LGPL-2.0"
                                            "LGPL-2.1"
                                            "LGPL-3.0"})

(defn- fix-gpl-only-or-later
  "If the set of ids includes both an 'only' and an 'or-later' variant of the
  same underlying GNU family identifier, remove the 'only' variant."
  [ids]
  (loop [result ids
         f      (first gpl-ids-with-only-or-later)
         r      (rest  gpl-ids-with-only-or-later)]
    (if f
      (recur (if (and (contains? result (str f "-only"))
                      (contains? result (str f "-or-later")))
               (disj result (str f "-only"))
               result)
             (first r)
             (rest r))
      result)))

(defn- fix-public-domain-cc0
  "If the set of ids includes both CC0-1.0 and lice-comb's public domain
  LicenseRef, remove the LicenseRef as it's redundant."
  [ids]
  (if (and (contains? ids (lcis/public-domain))
           (contains? ids "CC0-1.0"))
    (disj ids (lcis/public-domain))
    ids))

(defn- fix-mpl-2
  "If the set of ids includes both MPL-2.0 and MPL-2.0-no-copyleft-exception,
  remove the MPL-2.0-no-copyleft-exception as it's redundant."
  [ids]
  (if (and (contains? ids "MPL-2.0")
           (contains? ids "MPL-2.0-no-copyleft-exception"))
    (disj ids "MPL-2.0-no-copyleft-exception")
    ids))

(defn manual-fixes
  "Manually fix certain invalid combinations of license identifiers in a set."
  [ids]
  (when ids
    (some-> ids
            fix-gpl-only-or-later
            fix-public-domain-cc0
            fix-mpl-2
            set)))

(defmulti text->ids
  "Attempts to determine the SPDX license and/or exception identifier(s) (a set)
  within the given license text (a String, Reader, InputStream, or something
  that is accepted by clojure.java.io/reader - File, URL, URI, Socket, etc.).
  The result has metadata attached that describes how the identifiers were
  determined.

  Notes:
  * this function implements the SPDX matching guidelines (via clj-spdx).
    See https://spdx.github.io/spdx-spec/v2.3/license-matching-guidelines-and-templates/
  * the caller is expected to open & close a Reader or InputStream passed to
    this function (e.g. using clojure.core/with-open)
  * you cannot pass a String representation of a filename to this method - you
    should pass filenames through clojure.java.io/file first"
  {:arglists '([text])}
  type)

(defmethod text->ids java.lang.String
  [s]
  ; These clj-spdx APIs are *expensive*, so we paralellise them
  (let [f-lic    (future (sm/licenses-within-text   s @lcis/license-ids-d))
        f-exc    (future (sm/exceptions-within-text s @lcis/exception-ids-d))
        ids      (manual-fixes (set/union @f-lic @f-exc))]
    (when ids
      (with-meta ids (into {} (map #(vec [% {:type :concluded :confidence :high :strategy :spdx-matching}]) ids))))))

(defmethod text->ids java.io.Reader
  [r]
  (let [sw (java.io.StringWriter.)]
    (io/copy r sw)
    (text->ids (str sw))))

(defmethod text->ids java.io.InputStream
  [is]
  (text->ids (io/reader is)))

(defmethod text->ids :default
  [src]
  (when src
    (with-open [r (io/reader src)]
      (text->ids r))))

(defn- cdn-uri
  "Converts raw URIs into CDN URIs, for these 'known' hosts:

  * github.com e.g. https://github.com/pmonks/lice-comb/blob/main/LICENSE -> https://raw.githubusercontent.com/pmonks/lice-comb/main/LICENSE

  If the given URI is not known, returns the input unchanged."
  [uri]
  (if-let [^java.net.URL uri-obj (try (io/as-url uri) (catch Exception _ nil))]
    (case (s/lower-case (.getHost uri-obj))
      "github.com" (-> uri
                       (s/replace #"(?i)github\.com" "raw.githubusercontent.com")
                       (s/replace "/blob/"          "/"))
      uri)  ; Default case
    uri))

(defn- attempt-text-http-get
  "Attempts to get plain text as a String from the given URI, returning nil if
  unable to do so (including for error conditions - there is no way to
  disambiguate errors from non-text content, for example)."
  [uri]
  (when (lcu/valid-http-uri? uri)
    (try
      (when-let [response (hc/get (cdn-uri uri)
                                  {:http-client @http-client-d
                                   :accept      "text/plain;q=1,*/*;q=0"  ; Kindly request that the server only return text/plain... ...even though this gets ignored a lot of the time 🙄
                                   :header      {"user agent" "com.github.pmonks/lice-comb"}})]
        (when (= :text/plain (:content-type response))
          (:body response)))
      (catch Exception _
        nil))))

; TODO: THIS MAY BE UNNECESSARY AND IF SO SHOULD BE REMOVED
(comment
(defn listed-name->ids
  "Returns the SPDX license and/or exception identifier(s) (a set) for
  the given license name (matched case insensitively), or nil if there
  aren't any.

  Note that SPDX license names are not guaranteed to be unique - see
  https://github.com/spdx/license-list-XML/blob/main/DOCS/license-fields.md"
  [name]
  (when-not (s/blank? name)
    (get @lcis/index-name-to-id-d (s/trim (s/lower-case name)))))
)

(defn uri->ids
  "Returns the SPDX license and/or exception identifiers (a set) for the given
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

  The result has metadata attached that describes how the identifiers were
  determined."
  [uri]
  (when-not (s/blank? uri)
    (manual-fixes
      (let [suri (lcu/simplify-uri uri)]
        ; First, see if the URI string matches any of the URIs in the SPDX license list (using "simplified" URIs)
        (if-let [ids (get @lcis/index-uri-to-id-d suri)]
          (with-meta ids (into {} (map #(vec [% {:type :concluded :confidence :high :strategy :spdx-listed-uri :source (list uri)}]) ids)))
          ; Second, attempt to retrieve the text/plain contents of the uri and perform full license matching on it
          (when-let [license-text (attempt-text-http-get uri)]
            (when-let [ids (text->ids license-text)]
              (let [metadata (lcu/mapfonv #(assoc % :source (conj (:source %) (str uri "<retrieved text>"))) (meta ids))]  ; Append to existing metadata returned from text->ids
                (with-meta ids metadata)))))))))

(defn- string->ids-info
  "Converts the given String into a sequence of singleton maps, each of which
  has a key is that is an SPDX identifier (either a listed SPDX license or
  exception id if the value is recognised, or a lice-comb specific 'unlisted'
  LicenseRef if not), and whose value is meta-information about how that
  identifier was found. The result sequence is ordered in the same order of
  appearance as the source values in s.

  This involves:
  1. Seeing if it's a listed license or exception id
  2. Seeing if it's a listed license or exception name
  3. Checking if the value is a URI, and if so performing URI matching on it
  4. Using regexes to attempt to identify the license(s) and/or
     exception(s)
  5. Returning a lice-comb specific 'unlisted' LicenseRef"
  [s]
  (when-not (s/blank? s)
    ; 1. Is it an SPDX license or exception id?
    (let [s (s/trim s)]
      (if-let [id (get @lcis/spdx-ids-d (s/lower-case s))]
        (if (= id s)
          (list {id {:type :declared :strategy :spdx-listed-identifier-exact-match :source (list s)}})
          (list {id {:type :concluded :confidence :high :strategy :spdx-listed-identifier-case-insensitive-match :source (list s)}}))
        ; 2. Is it an SPDX license or exception name?
        (if-let [ids (get @lcis/index-name-to-id-d (s/trim (s/lower-case s)))]
          (map #(hash-map % {:type :concluded :confidence :low :strategy :spdx-listed-name :source (list s)}) ids)
          ; 3. Is it a URI?  If so, perform URI matching on it (this is to handle some dumb corner cases that exist in pom.xml files hosted on Clojars & Maven Central)
          (if-let [ids (uri->ids s)]
            (mapcat #(list {(key %) (val %)}) (meta ids))
            ; 4. Attempt regex name matching
            (if-let [ids (lcirm/match-regexes s)]
              (map #(hash-map % {:type :concluded :confidence :low :strategy :regex-matching :source (list s)}) ids)
              ; 5. Give up and return a lice-comb "unlisted" LicenseRef
              (list {(lcis/name->unlisted s) {:type :concluded :confidence :low :strategy :unlisted :source (list s)}}))))))))

(defn- filter-blanks
  "Filter blank strings out of coll"
  [coll]
  (when (seq coll)
    (seq (filter #(or (not (string? %)) (not (s/blank? %))) coll))))

(defn- map-split-and-interpose
  "Maps over the given sequence, splitting strings using the given regex
  and interposing the given value, returning a (flattened) sequence."
  [re int coll]
  (mapcat #(if-not (string? %)
             [%]
             (let [splits (s/split % re)]
               (if (nil? int)
                 splits
                 (interpose int splits))))
          coll))

(defn split-on-operators
  "Case insensitively splits a string based on license operators (and,
  or, with), but only if they're not also part of a license name (e.g.
  'Common Development and Distribution License', 'GNU General Public
  License version 2.0 or (at your option) any later version', etc.)."
  [s]
  (when-not (s/blank? s)
    (->> (s/split (s/trim s) #"(?i)\band[/-\\]+or\b")
         (map-split-and-interpose #"(?i)(\band|\&)(?!\s+(distribution|all\s+rights\s+reserved))"                                                                :and)
         (map-split-and-interpose #"(?i)\bor(?!\s*(-?later|lator|newer|lesser|library|\(?at\s+your\s+(option|discretion)\)?|([\"']?(Revised|Modified)[\"']?)))" :or)
         (map-split-and-interpose #"(?i)\b(with|w/)(?!\s+the\s+acknowledgment\s+clause\s+removed)"                                                              :with)
         filter-blanks
         (map #(if (string? %) (s/trim %) %)))))

(def ^:private push conj)   ; With lists-as-stacks conj == push

(defn- process-expression-element
  "Processes a single new expression element e (either a keyword representing
  an SPDX operator, or an SPDX identifier) in the context of stack (list) s."
  [s e]
  (if (keyword? e)
    ; e is a keyword (SPDX operator): only push a keyword if the prior element was an id, or it's different to the prior keyword
    (if (= (peek s) e)
      s
      (push s e))
    ; e is a singleton map with an SPDX identifier as a key: depending on how many keywords are currently at the top of s...
    (case (count (take-while keyword? s))
      ; No keywords? Push e onto s
      0 (push s e)
      ; One keyword? See if we should "collapse" the prior value, the keyword and e into an SPDX expression fragment and push the result onto s
      1 (let [kw        (peek s)
              operator  (s/upper-case (name kw))
              s-minus-1 (pop s)
              prior     (peek s-minus-1)
              s-minus-2 (pop s-minus-1)]
          (if (nil? prior)
            (push s-minus-2 e)       ; s had one keyword on it (which is invalid), so drop it and push e on
            (if (or (not= :with kw)  ; If the prior keyword was :and or :or, or :with and the current element is a listed exception id, build an SPDX expression fragment and push the result onto s
                    (se/listed-id? e))
              (push s-minus-2 (s/join " " [prior operator e]))
              (push s-minus-1 e))))  ; We had a :with operator without a valid exception id following it, so simply drop the :with keyword from the stack and push the current element on
      ; Many keywords? That's invalid (since we dedupe them when they get pushed on, so this means they're different), so drop all of them and push e onto s
      (push (drop-while keyword? s) e))))

(defn- build-spdx-expressions
  "Builds a set of SPDX expressions from the given list of strings & keywords."
  [l]
  (loop [result '()
         f      (first l)
         r      (rest l)]
    (if f
      (recur (process-expression-element result f) (first r) (rest r))
      (some-> (seq (reverse result))  ; Remember to reverse the expressions, since lists-as-stacks grow at the front, not the end
              set
              manual-fixes))))

(defn attempt-to-build-expressions
  "Attempts to build SPDX expression(s) (a set of strings) from the
  given name. The result has metadata attached that describes how the
  identifiers were determined."
  [name]
  (when-let [partial-expressions (some->> (split-on-operators name)
                                          (drop-while keyword?)
                                          (lc3/rdrop-while keyword?)
                                          (map #(if (keyword? %) % (string->ids-info %)))
                                          flatten
                                          seq)]
    (let [spdx-expressions (build-spdx-expressions (map #(if (keyword? %) % (first (keys %))) partial-expressions))
          metadata         (into {} (filter (complement keyword?) partial-expressions))]
      (with-meta spdx-expressions metadata))))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it.

  Note: this method has a substantial performance cost."
  []
  (lcis/init!)
  (lcirm/init!)
  @http-client-d
  nil)
