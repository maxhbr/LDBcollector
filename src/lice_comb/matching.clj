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
  "Matching functionality, some of which is provided by
  https://github.com/pmonks/clj-spdx"
  (:require [clojure.string        :as s]
            [clojure.set           :as set]
            [clojure.java.io       :as io]
            [hato.client           :as hc]
            [spdx.licenses         :as sl]
            [spdx.exceptions       :as se]
            [spdx.matching         :as sm]
            [spdx.expressions      :as sexp]
            [rencg.api             :as rencg]
            [lice-comb.impl.utils  :as lcu]))

; The license and exception lists
(def ^:private license-list-d   (delay (map sl/id->info (sl/ids))))
(def ^:private exception-list-d (delay (map se/id->info (se/ids))))

; The unlisted license refs lice-comb uses (note: the unlisted one usually has a base62 suffix appended)
(def ^:private public-domain-license-ref   "LicenseRef-lice-comb-PUBLIC-DOMAIN")
(def ^:private unlisted-license-ref-prefix "LicenseRef-lice-comb-UNLISTED")

(defn public-domain?
  "Is the given id lice-comb's custom 'public domain' LicenseRef?"
  [id]
  (= (s/lower-case id) (s/lower-case public-domain-license-ref)))

(def ^{:doc "Constructs a valid SPDX id (a LicenseRef specific to lice-comb)
  representing public domain."
       :arglists '([])}
  public-domain
  (constantly public-domain-license-ref))

(defn unlisted?
  "Is the given id a lice-comb custom 'unlisted' LicenseRef?"
  [id]
  (when id
    (s/starts-with? (s/lower-case id) (s/lower-case unlisted-license-ref-prefix))))

(defn name->unlisted
  "Constructs a valid SPDX id (a LicenseRef specific to lice-comb) for an
  unlisted license, with the given name appended as Base62 (since clj-spdx
  identifiers are basically constrained to [A-Z][a-z][0-9] ie. Base62)."
  [name]
  (str unlisted-license-ref-prefix (when-not (s/blank? name) (str "-" (lcu/base62-encode name)))))

(defn unlisted->name
  "Get the original name of the given unlisted license. Returns nil if id is nil
  or is not a lice-comb's unlisted LicenseRef."
  [id]
  (when (unlisted? id)
    (str "Unlisted ("
         (if (> (count id) (count unlisted-license-ref-prefix))
           (lcu/base62-decode (subs id (+ 2 (count unlisted-license-ref-prefix))))
           "-original name not available-")
          ")")))

(defn id->name
  "Returns the human readable name of the given license or exception identifier;
  either the official SPDX license or exception name or, if the id is a
  lice-comb specific LicenseRef, a lice-comb specific name. Returns the id
  verbatim if unable to determine a name. Returns nil if the id is blank."
  [id]
  (when-not (s/blank? id)
    (cond (sl/listed-id? id)  (:name (sl/id->info id))
          (se/listed-id? id)  (:name (se/id->info id))
          (public-domain? id) "Public domain"
          (unlisted? id)      (unlisted->name id)
          :else               id)))

(defmulti text->ids
  "Attempts to determine the SPDX license and/or exception identifier(s) (a set)
  within the given license text (a String, Reader, InputStream, or something
  that is accepted by clojure.java.io/reader - File, URL, URI, Socket, etc.).

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
  (let [f-lic (future (sm/licenses-within-text   s))
        f-exc (future (sm/exceptions-within-text s))]
    (set/union @f-lic @f-exc)))

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

(defn- urls-to-id-tuples
  "Extracts all urls for a given list (license or exception) entry."
  [list-entry]
  (let [id              (:id list-entry)
        simplified-uris (map lcu/simplify-uri (filter (complement s/blank?) (concat (:see-also list-entry) (get-in list-entry [:cross-refs :url]))))]
    (map #(vec [% id]) simplified-uris)))

(def ^:private index-uri-to-id-d (delay (merge (lcu/mapfonv #(lcu/nset (map second %)) (group-by first (mapcat urls-to-id-tuples @license-list-d)))
                                               (lcu/mapfonv #(lcu/nset (map second %)) (group-by first (mapcat urls-to-id-tuples @exception-list-d))))))

(def ^:private http-client-d (delay (hc/build-http-client {:connect-timeout 1000
                                                           :redirect-policy :always
                                                           :cookie-policy   :none})))

(defn- github-raw-uri
  "Converts a GitHub 'UI' URI into a 'raw' (CDN) GitHub URI.

  e.g. https://github.com/pmonks/lice-comb/blob/main/LICENSE -> https://raw.githubusercontent.com/pmonks/lice-comb/main/LICENSE

  If the given URI is not a GitHub 'UI' URI, returns the URI unchanged."
  [uri]
  (if-let [uri-obj (try (io/as-url uri) (catch Exception _ nil))]
    (if (= "github.com" (s/lower-case (.getHost uri-obj)))
      (-> uri
          (s/replace "github.com" "raw.githubusercontent.com")
          (s/replace "/blob/"     "/"))
      uri)
    uri))

(defn- attempt-text-http-get
  "Attempts to get plain text as a String from the given URI, returning nil if
  unable to do so (including for error conditions - there is no way to
  disambiguate errors from non-text content, for example)."
  [uri]
  (when (lcu/valid-http-uri? uri)
    (try
      (when-let [response (hc/get (github-raw-uri uri)
                                  {:http-client @http-client-d
                                   :accept      "text/plain;q=1,*/*;q=0"})]  ; Kindly request server to only return text/plain... ...even though this gets ignored a lot of the time 🙄
        (when (= :text/plain (:content-type response))
          (:body response)))
      (catch Exception _
        nil))))

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
     may represent multiple licenses and/or exceptions."
  [uri]
  (when-let [suri (lcu/simplify-uri uri)]
    ; First, see if the URI string matches any of the URIs in the SPDX license list (using "simplified" URIs)
    (if-let [result (get @index-uri-to-id-d suri)]
      result
      ; Second, attempt to retrieve it as text/plain and perform full license matching on it
      (when-let [license-text (attempt-text-http-get uri)]
        (text->ids license-text)))))

(defn- name-to-id-tuple
  [list-entry]
  [(s/lower-case (s/trim (:name list-entry))) (:id list-entry)])

(def ^:private index-name-to-id-d (delay (merge (lcu/mapfonv #(lcu/nset (map second %)) (group-by first (map name-to-id-tuple @license-list-d)))
                                                (lcu/mapfonv #(lcu/nset (map second %)) (group-by first (map name-to-id-tuple @exception-list-d))))))

(defn- listed-name->ids
  "Returns the SPDX license and/or exception identifier(s) (a set) for the given license name
  (matched case insensitively), or nil if there aren't any.

  Note that SPDX license names are not guaranteed to be unique - see
  https://github.com/spdx/license-list-XML/blob/main/DOCS/license-fields.md"
  [name]
  (when-not (s/blank? name)
    (get @index-name-to-id-d (s/trim (s/lower-case name)))))

(defn- parse-expression-and-extract-ids
  "Parse s as if it were an SPDX expression, and if it is, extract all ids
  (for licenses and exceptions) out of it."
  [s]
  (when-let [expression (sexp/parse s)]
    (sexp/extract-ids expression)))

(defn- get-rencgs
  "Get a value for an re-ncg, potentially looking at multiple ncgs in order until a non-blank value is found. Also trims and lower-cases the value."
  ([m names] (get-rencgs m names nil))
  ([m names default]
    (loop [f (first names)
           r (rest  names)]
      (if f
        (let [value (get m f)]
          (if (s/blank? value)
            (recur (first r) (rest r))
            (s/lower-case (s/trim value))))
        default))))

;####TODO: MAKE THIS FUNCTION RETURN METADATA ABOUT :concluded VS :declared AS WELL AS SOURCE!!!!
(defn- generic-id-constructor
  [m]
  (when m
    (str (:id m)
         (when-let [ver (get-rencgs m ["version"] (:latest-ver m))]
           (str "-"
                ver
                (when (and (:pad-ver? m)
                           (not (s/includes? ver ".")))
                  (let [pad (last (s/split (:latest-ver m) #"\."))]
                    (when-not (s/blank? pad)
                      (str "." pad)))))))))

(defn- number-name-to-number
  "Converts the name of a number to that number (as a string). e.g. \"two\" -> \"2\".  Returns s unchanged if it's not a number name."
  [^String s]
  (when s
    (case s
      "two"   "2"
      "three" "3"
      "four"  "4"
      s)))

(defn- is-digits?
  "Does the given string contains digits only?"
  [^String s]
  (boolean  ; Eliminate nil-punning, since we use the output of this method in case
    (when s
      (every? #(Character/isDigit ^Character %) s))))

;####TODO: MAKE THIS FUNCTION RETURN METADATA ABOUT :concluded VS :declared AS WELL AS SOURCE!!!!
(defn- bsd-id-constructor
  [m]
  (let [clause-count1          (number-name-to-number (get-rencgs m ["clausecount1"]))
        clause-count2          (number-name-to-number (get-rencgs m ["clausecount2"]))
        preferred-clause-count (case [(is-digits? clause-count1) (is-digits? clause-count2)]
                                 [true true]   clause-count1
                                 [true false]  clause-count1
                                 [false true]  clause-count2
                                 (if (contains? #{"simplified" "new" "revised" "modified" "aduna"} clause-count1)
                                   clause-count1
                                   clause-count2))
        clause-count           (case preferred-clause-count
                                 ("2" "simplified")                       "2"
                                 ("3" "new" "revised" "modified" "aduna") "3"
                                 "4")] ; Note: we default to 4 clause, since it was the original form of the BSD license
    (str (:id m) "-" clause-count "-Clause")))

;####TODO: MAKE THIS FUNCTION RETURN METADATA ABOUT :concluded VS :declared AS WELL AS SOURCE!!!!
(defn- cc-id-constructor
  [m]
  (let [nc?            (not (s/blank? (get-rencgs m ["noncommercial"])))
        nd?            (not (s/blank? (get-rencgs m ["noderivatives"])))
        sa?            (not (s/blank? (get-rencgs m ["sharealike"])))
        version        (get-rencgs m ["version"] (:latest-ver m))
        base-id        (str "CC-BY-"
                         (when nc?                 "NC-")
                         (when nd?                 "ND-")
                         (when (and (not nd?) sa?) "SA-")   ; SA and ND are incompatible (and have no SPDX id as a result), and if both are (erroneously) specified we conservatively choose ND
                         version)
        region         (case (get-rencgs m ["region"])
                         "australia"                                            "AU"
                         "austria"                                              "AT"
                         ("england" "england and wales" "england & wales" "uk") "UK"
                         "france"                                               "FR"
                         "germany"                                              "DE"
                         "igo"                                                  "IGO"
                         "japan"                                                "JP"
                         "netherlands"                                          "NL"
                         ("united states" "usa" "us")                           "US"
                         nil)
        id-with-region (str base-id (when-not (s/blank? region) (str "-" region)))]
    (if (contains? (sl/ids) id-with-region)  ; Not all license variants and versions have a region specific identifier, so check that it's valid before returning it
      id-with-region
      (if (contains? (sl/ids) base-id)
        base-id
        (throw (ex-info "Invalid Creative Commons license information found" (dissoc m :id :regex :fn :pad-ver? :latest-ver)))))))

;####TODO: MAKE THIS FUNCTION RETURN METADATA ABOUT :concluded VS :declared AS WELL AS SOURCE!!!!
(defn- gpl-id-constructor
  [m]
  (let [id      (case (get-rencgs m ["edition1" "edition2"])
                  ("affero" "agpl")           "AGPL"
                  ("lesser" "library" "lgpl") "LGPL"
                  "GPL")
        version (let [ver (get-rencgs m ["version"] (:latest-ver m))]
                  (if (s/includes? ver ".")
                    ver
                    (str ver ".0")))
        suffix  (case (get-rencgs m ["suffix"])
                  ("later" "newer" "+") "or-later"
                  ("only")              "only"
                  "only")]  ; Note: we (conservatively) default to "only" when we don't have an explicit suffix
    (str id "-" version (when-not (= id "AGPL") (str "-" suffix)))))

(defn- simple-regex-match
  "Constructs a 'simple' name match structure"
  [s]
  {:id    s
   :regex (re-pattern (str "(?i)\\b" s "\\b"))
   :fn    (constantly s)})

; Regexes used for license name matching, along with functions for constructing an SPDX id
(def ^:private license-name-matching (concat
  ; By default we add every single id as a "simple" regex match, excluding MIT and Zlib (they're explicitly handled below)
  (map simple-regex-match (disj (sl/ids) "MIT" "Zlib"))
  (map simple-regex-match (se/ids))
  [
  {:id         "AFL"
   :regex      #"(?i)\bAcademic(\s+Free)?(\s+Licen[cs]e)?[\s,-]*(\s*V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?\b"
   :fn         generic-id-constructor
   :pad-ver?   true
   :latest-ver "3.0"}
  {:id         "Apache"
   :regex      #"(?i)\b(ASL|Apache)(\s+Software)?(\s+Licen[cs]e(s)?)?[\s,-]*(\s*V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?\b"
   :fn         generic-id-constructor
   :pad-ver?   true
   :latest-ver "2.0"}
  {:id         "Artistic"
   :regex      #"(?i)\bArtistic\s+Licen[cs]e(\s*V(ersion)?)?[\s,-]*(?<version>\d+(\.\d+)?)?\b"
   :fn         generic-id-constructor
   :pad-ver?   true
   :latest-ver "2.0"}
  {:id         "Beerware"
   :regex      #"(?i)\bBeer-?ware\b"
   :fn         (constantly "Beerware")}
  {:id         "BSL"
   :regex      #"(?i)\bBoost(\s+Software)?(\s+Licen[cs]e)?[\s,-]*(?<version>\d+(\.\d+)?)?\b"
   :fn         generic-id-constructor
   :pad-ver?   true
   :latest-ver "1.0"}
  {:id         "BSD"
   :regex      #"(?i)\b(?<clausecount1>\p{Alnum}+)?[\s,-]*(C(lause)?|Type)?\s*\bBSD[\s-]*\(?(Type|C(lause)?)?[\s-]*(?<clausecount2>\p{Alnum}+)?"
   :fn         bsd-id-constructor}
  {:id         "CC0"
   :regex      #"(?i)\bCC\s*0"
   :fn         (constantly "CC0-1.0")}
  {:id         "CECILL"
   :regex      #"(?i)\bCeCILL(\s+Free)?(\s+Software)?(\s+Licen[cs]e)?(\s+Agreement)?[\s,-]*(\s*V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?\b"
   :fn         generic-id-constructor
   :pad-ver?   true
   :latest-ver "2.1"}
  {:id         "Classpath-exception"
   :regex      #"(?i)\bClasspath[\s-]+exception(\s*V(ersion)?)?[\s-]*(?<version>\d+(\.\d+)?)?\b"
   :fn         generic-id-constructor
   :pad-ver?   true
   :latest-ver "2.0"}
  {:id         "CDDL"
   :regex      #"(?i)(CDDL|Common\s+Development\s+(and|\&)?\s+Distribution\s+Licen[cs]e)(\s+\(?CDDL\)?)?[\s,-]*(\s*V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?\b"
   :fn         generic-id-constructor
   :pad-ver?   true
   :latest-ver "1.1"}
  {:id         "CPL"
   :regex      #"(?i)Common\s+Public\s+Licen[cs]e[\s,-]*(\s*V(ersion)?)?(?<version>\d+(\.\d+)?)?\b"
   :fn         generic-id-constructor
   :pad-ver?   true
   :latest-ver "1.0"}
  {:id         "Creative commons family"
   :regex      #"(?i)\b(CC([\s-]+BY)?\b|(Creative\s+Commons\s+(Attribution)?|Attribution))([\s,-]*((?<noncommercial>Non\s*Commercial|NC)|(?<noderivatives>No[\s-]*Deriv(ative)?s?|ND)|(?<sharealike>Share[\s-]*Alike|SA)))*(\s+Unported|International|Generic)?(\s+Licen[cs]e)?[\s,-]*(\s*V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?(?<region>Australia|Austria|England((\s+and|\&)?\s+Wales)?|France|Germany|IGO|Japan|Netherlands|UK|United\s+States|USA?)?\b"
   :fn         cc-id-constructor
   :pad-ver?   true
   :latest-ver "4.0"}
  {:id         "EPL"   ; Eclipse Public License (EPL) - v 1.0
   :regex      #"(?i)\b(EPL|Eclipse(\s+Public)?(\s+Licen?[cs]e)?)(\s*\(EPL\))?[\s,-]*(V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?\b"   ; Note: optional "n" in "license" is because of a known typo
   :fn         generic-id-constructor
   :pad-ver?   true
   :latest-ver "2.0"}
  {:id         "EUPL"
   :regex      #"(?i)\bEuropean\s+Union(\s+Public)?(\s+Licen[cs]e)?[\s,-]*(\(?EUPL\)?)?[\s,-]*(V(ersion)?)?(\.)?\s*(?<version>\d+(\.\d+)?)?\b"
   :fn         generic-id-constructor
   :pad-ver?   true
   :latest-ver "1.2"}
  {:id         "FreeBSD"
   :regex      #"(?i)\bFreeBSD\b"
   :fn         (constantly "BSD-2-Clause-FreeBSD")}
  {:id         "GNU license family"
   :regex      #"(?i)\b(?<edition1>(Affero|Lesser|Library|LGPL|AGPL)\s+)?(GPL|GNU|General\s+Pub?lic\s+Licen[cs]e)(?<edition2>\s+(Affero|Lesser|Library))?(\s+General)?(\s+Public)?(\s+Licen[cs]e)?(\s+\(?(A|L)?GPL\)?)?([\s,-]*V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?\s*(or(\s+\(?at\s+your\s+option\)?)?)?(\s+any)?(\s*(?<suffix>later|newer|only|\+))?\b"
   :fn         gpl-id-constructor
   :pad-ver?   true
   :latest-ver 3.0}
  {:id         "Hippocratic"
   :regex      #"(?i)\bHippocratic\b"
   :fn         (constantly "Hippocratic-2.1")}  ; There are no other listed versions of this license
  {:id         "LLVM-exception"
   :regex      #"(?i)\bLLVM[\s-]+Exception\b"
   :fn         (constantly "LLVM-exception")}
  {:id         "MIT"
   :regex      #"(?i)\bMIT(?![\s/]*(X11|ISC))(\s+Public)?(\s+Licen[cs]e)?\b"
   :fn         (constantly "MIT")}
  {:id         "MPL"
   :regex      #"(?i)\b(MPL|Mozilla)(\s+Public)?(\s+Licen[cs]e)?[\s,-]*(V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?\b"
   :fn         generic-id-constructor
   :pad-ver?   true
   :latest-ver "2.0"}
  {:id         "NASA"
   :regex      #"(?i)\bNASA(\s+Open)?(\s+Source)?(\s+Agreement)?[\s,-]+(V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?\b"
   :fn         generic-id-constructor
   :pad-ver?   true
   :latest-ver "1.3"}
  {:id         "Public Domain"
   :regex      #"(?i)\bPublic\s+Domain(?![\s\(]*CC\s*0)"
   :fn         (constantly public-domain-license-ref)}
  {:id         "Ruby"
   :regex      #"(?i)\bRuby(\s+Licen[cs]e)?\b"
   :fn         (constantly "Ruby")}
  {:id         "SGI-B"
   :regex      #"(?i)\bSGI(\s+Free)?(\s+Software)?(\s+Licen[cs]e)?([\s,-]+(V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?)?\b"
   :fn         generic-id-constructor
   :pad-ver?   true
   :latest-ver "2.0"}
  {:id         "Unlicense"
   :regex      #"(?i)\bUnlicen[cs]e\b"
   :fn         (constantly "Unlicense")}
  {:id         "WTFPL"
   :regex      #"(?i)\b(WTFPL|DO-WTF-U-WANT-2|Do\s+What\s+The\s+Fuck\s+You\s+Want\s+To(\s+Public)?(\s+Licen[cs]e)?)\b"
   :fn         (constantly "WTFPL")}
  {:id         "Zlib"
   :regex      #"\b(?i)zlib(?![\s/]+libpng)\b"
   :fn         (constantly "Zlib")}
  ]))

;####TODO: MAKE THIS FUNCTION RETURN METADATA ABOUT :concluded VS :declared AS WELL AS SOURCE!!!!
(defn- match-regex
  "Returns the SPDX license-id for the given elem from license-name-matching, if a match occurred, or nil if there was no match."
  [name elem]
  (when-let [matches (rencg/re-find-ncg (:regex elem) name)]
    ((:fn elem) (merge {:name name} elem matches))))

;####TODO: MAKE THIS FUNCTION RETURN METADATA ABOUT :concluded VS :declared AS WELL AS SOURCE!!!!
(defn- match-regexes
  "Returns all of the matched SPDX license-id for the given name, or nil if there were no matches."
  [name]
  (some-> (seq (filter identity (pmap (partial match-regex name) license-name-matching)))
          set))

(defn- fix-public-domain-cc0
  [ids]
  (if (and (contains? ids public-domain-license-ref)
           (contains? ids "CC0-1.0"))
    (disj ids public-domain-license-ref)
    ids))

(defn- fix-classpath-exception
  [ids]
  (if (contains? ids "GPL-2.0-with-classpath-exception")
    (conj (disj ids "GPL-2.0-with-classpath-exception") "GPL-2.0-only" "Classpath-exception-2.0")
    ids))

(defn- manual-fixes
  "Manually fix certain combinations of license identifiers."
  [ids]
  (when ids
    (-> ids
        fix-public-domain-cc0
        fix-classpath-exception)))

;####TODO: MAKE THIS FUNCTION RETURN METADATA ABOUT :concluded VS :declared AND SOURCE!!!!
(defn name->ids
  "Attempts to determine the SPDX license identifier(s) (a set) from the given
  name (a string), or nil if there aren't any.  This involves:
  1. checking if the name is actually an SPDX expression (this is rare, but
     sometimes an SPDX identifier or expression appears in a pom.xml file)
  2. looking up the name case insensitively in the SPDX license list
  3. matching lice-comb specific 'name matching' regexes against the name
  4. if the name is actually a URI, running it through uri->ids

  If those steps all fail, a lice-comb custom 'unlisted' LicenseRef is returned
  instead (which can be checked using the unlisted? fn)."
  [name]
  (when-not (s/blank? name)
    (manual-fixes
      (let [name (s/trim name)]
        ; 1. Parse the name as an SPDX exception, and if that succeeds, return all ids in the expression
        (if-let [ids-in-expression (parse-expression-and-extract-ids name)]
          ids-in-expression
          ; 2. Then we look up by name
          (if-let [listed-name-matches (listed-name->ids name)]
            listed-name-matches
            ; 3. Then we fallback on regex name matching
            (if-let [re-name-matches (match-regexes name)]
              re-name-matches
              ; 4. Then we see if it's actually a URI, and URI match if so - this is to handle some dumb corner cases that exist in the real world
              (if-let [uri-matches (uri->ids name)]
                uri-matches
                #{(name->unlisted name)}))))))))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it.

  Note: this method has a substantial performance cost."
  []
  (sl/init!)
  (se/init!)
  @license-list-d
  @exception-list-d
  @index-uri-to-id-d
  @index-name-to-id-d
  @http-client-d
  nil)
