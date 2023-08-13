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
(def ^:private public-domain-license-ref          "LicenseRef-lice-comb-PUBLIC-DOMAIN")
(def ^:private proprietary-commercial-license-ref "LicenseRef-lice-comb-PROPRIETARY-OR-COMMERCIAL")
(def ^:private unlisted-license-ref-prefix        "LicenseRef-lice-comb-UNLISTED")

; Lower case id map
(def ^:private spdx-ids-d (delay (merge (into {} (map #(vec [(s/lower-case %) %]) (sl/ids)))
                                        (into {} (map #(vec [(s/lower-case %) %]) (se/ids))))))

(defn public-domain?
  "Is the given id lice-comb's custom 'public domain' LicenseRef?"
  [id]
  (= (s/lower-case id) (s/lower-case public-domain-license-ref)))

(def ^{:doc "Constructs a valid SPDX id (a LicenseRef specific to lice-comb)
  representing public domain."
       :arglists '([])}
  public-domain
  (constantly public-domain-license-ref))

(defn proprietary-or-commercial?
  "Is the given id lice-comb's custom 'proprietary or commercial' LicenseRef?"
  [id]
  (= (s/lower-case id) (s/lower-case proprietary-commercial-license-ref)))

(def ^{:doc "Constructs a valid SPDX id (a LicenseRef specific to lice-comb)
  representing a proprietary or commercial license."
       :arglists '([])}
  proprietary-or-commercial
  (constantly proprietary-commercial-license-ref))

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
    (cond (sl/listed-id? id)              (:name (sl/id->info id))
          (se/listed-id? id)              (:name (se/id->info id))
          (public-domain? id)             "Public domain"
          (proprietary-or-commercial? id) "Proprietary or commercial"
          (unlisted? id)                  (unlisted->name id)
          :else                           id)))

(defn- fix-public-domain-cc0
  [ids]
  (if (and (contains? ids public-domain-license-ref)
           (contains? ids "CC0-1.0"))
    (disj ids public-domain-license-ref)
    ids))

(defn- fix-ids-that-end-with-plus
  [ids]
  (some-> (seq (map #(s/replace % #"\+\z" "-or-later") ids))   ; Note: assumes that all SPDX license identifiers that end in '+' also have a variant that ends in '-or-later' (which is known to be true up to 2023-07-01, and I expect to remain true going forward thanks to SPDX expressions)
          set))

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
        fix-ids-that-end-with-plus
        fix-classpath-exception)))

; Only match against SPDX license identifiers that do _not_ end with "+" - these are all duplicate/old/deprecated ids that pre-date license expressions (where "+" gained independent semantics)
(def ^:private license-ids-for-matching-d (delay (filter #(not (s/ends-with? % "+")) (sl/ids))))

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
  (let [f-lic (future (sm/licenses-within-text   s @license-ids-for-matching-d))
        f-exc (future (sm/exceptions-within-text s))]
    (manual-fixes (set/union @f-lic @f-exc))))

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
  "Converts a GitHub UI URI into a GitHub CDN URI.
  e.g. https://github.com/pmonks/lice-comb/blob/main/LICENSE -> https://raw.githubusercontent.com/pmonks/lice-comb/main/LICENSE

  If the given URI is not a GitHub UI URI, returns the input unchanged."
  [uri]
  (if-let [^java.net.URL uri-obj (try (io/as-url uri) (catch Exception _ nil))]
    (if (= "github.com" (s/lower-case (.getHost uri-obj)))
      (-> uri
          (s/replace #"(?i)github\.com" "raw.githubusercontent.com")
          (s/replace "/blob/"          "/"))
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
                                   :accept      "text/plain;q=1,*/*;q=0"  ; Kindly request that the server only return text/plain... ...even though this gets ignored a lot of the time 🙄
                                   :header      {"user agent" "com.github.pmonks/lice-comb"}})]
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
  (when-not (s/blank? uri)
    (manual-fixes
      (let [suri (lcu/simplify-uri uri)]
        ; First, see if the URI string matches any of the URIs in the SPDX license list (using "simplified" URIs)
        (if-let [result (get @index-uri-to-id-d suri)]
          result
          ; Second, attempt to retrieve the text/plain contents of the uri and perform full license matching on it
          (when-let [license-text (attempt-text-http-get uri)]
            (text->ids license-text)))))))

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
  "Get a value for an re-ncg, potentially looking at multiple ncgs in order until a non-blank value is found. Also trims and lower-cases the value, and replaces all whitespace with a single space."
  ([m names] (get-rencgs m names nil))
  ([m names default]
    (loop [f (first names)
           r (rest  names)]
      (if f
        (let [value (get m f)]
          (if (s/blank? value)
            (recur (first r) (rest r))
            (-> value
                (s/trim)
                (s/lower-case)
                (s/replace #"\s+" " "))))
        default))))

(defn- generic-id-constructor
  [m]
  (when m
    (str (:id m)
         (when-let [ver (get-rencgs m ["version"] (:latest-ver m))]
           (str "-"
                ver
                (when (and (:pad-ver? m)
                           (not (s/includes? ver ".")))
                  ".0"))))))

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
                                 "4")  ; Note: we default to 4 clause, since it was the original form of the BSD license
        suffix                 (case (get-rencgs m ["suffix"])
                                 "patent"                                              "Patent"
                                 "views"                                               "Views"
                                 "attribution"                                         "Attribution"
                                 "clear"                                               "Clear"
                                 "lbnl"                                                "LBNL"
                                 "modification"                                        "Modification"
                                 ("no military license" "no military licence")         "No-Military-License"
                                 ("no nuclear license" "no nuclear licence")           "No-Nuclear-License"
                                 ("no nuclear license 2014" "no nuclear licence 2014") "No-Nuclear-License-2014"
                                 "no nuclear warranty"                                 "No-Nuclear-Warranty"
                                 "open mpi"                                            "Open-MPI"
                                 "shortened"                                           "Shortened"
                                 "uc"                                                  "UC"
                                 nil)
        base-id                (str (:id m) "-" clause-count "-Clause")
        id-with-suffix         (str base-id "-" suffix)]
    (if (contains? (sl/ids) id-with-suffix)  ; Not all suffixes are valid with all BSD clause counts, so check that it's valid before returning it
      id-with-suffix
      base-id)))

(defn- cc-id-constructor
  [m]
  (let [nc?            (not (s/blank? (get-rencgs m ["noncommercial"])))
        nd?            (not (s/blank? (get-rencgs m ["noderivatives"])))
        sa?            (not (s/blank? (get-rencgs m ["sharealike"])))
        version        (get-rencgs m ["version1" "version2"] (:latest-ver m))
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
    (str id "-" version  "-" suffix)))

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
   :regex      #"(?i)\b(ASL|Apache)(\s+Software)?(\s+Licen[cs]e(s)?)?[\s,-]*(\s*V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?(?!.*acknowledgment\s+clause\s+removed)\b"
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
   :regex      #"(?i)\b(?<clausecount1>\p{Alnum}+)?[\s,-]*(C(lause)?|Type)?\s*\bBSD[\s-]*\(?(Type|C(lause)?)?[\s-]*(?<clausecount2>\p{Alnum}+)?([\s-]+Clause)?(?<suffix>\s+(Patent|Views|Attribution|Clear|LBNL|Modification|No\s+Military\s+Licen[cs]e|No\s+Nuclear\s+Licen[cs]e([\s-]+2014)?|No\s+Nuclear\s+Warranty|Open\s+MPI|Shortened|UC))?"
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
   :regex      #"(?i)\b(CC([\s-]+BY)?\b|(Creative\s+Commons(\s+Legal\s+Code)?(\s+Attribution)?|Attribution\s+(?<version1>\d(.\d)?)))([\s,-]*((?<noncommercial>Non\s*Commercial|NC)|(?<noderivatives>No[\s-]*Deriv(ative)?s?|ND)|(?<sharealike>Share[\s-]*Alike|SA)))*(\s+Unported|International|Generic)?(\s+Licen[cs]e)?[\s,-]*(\s*V(ersion)?)?\s*(?<version2>\d+(\.\d+)?)?(?<region>Australia|Austria|England((\s+and|\&)?\s+Wales)?|France|Germany|IGO|Japan|Netherlands|UK|United\s+States|USA?)?\b"
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
   :regex      #"(?i)\b(?<edition1>(Affero|Lesser|Library|LGPL|AGPL)\s+)?(GPL|GNU(?!\s*Classpath)|General\s+Pub?lic\s+Licen[cs]e)(?<edition2>\s+(Affero|Lesser|Library))?(\s+General)?(\s+Public)?(\s+Licen[cs]e)?(\s+\(?(A|L)?GPL\)?)?([\s,-]*V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?\s*(or(\s+\(?at\s+your\s+(option|discretion)\)?)?)?(\s+any)?(\s*(?<suffix>later|newer|only|\+))?\b"
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
   :regex      #"(?i)\b(MIT|Bouncy\s+Castle)(?![\s/]*(X11|ISC))(\s+Public)?(\s+Licen[cs]e)?\b"
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
  {:id         "Plexus"
   :regex      #"(?i)\bApache\s+Licen[cs]e(\s+but)?(\s+with)?(\s+the)?\s+acknowledgment\s+clause\s+removed\b"
   :fn         (constantly "Plexus")}
  {:id         "Proprietary or commercial"
   :regex      #"(?i)\b(Propriet[ao]ry|Commercial|All\s+Rights\s+Reserved|Private)\b"
   :fn         proprietary-or-commercial}
  {:id         "Public Domain"
   :regex      #"(?i)\bPublic\s+Domain(?![\s\(]*CC\s*0)"
   :fn         public-domain}
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

(defn- match-regex
  "Returns a map containing the SPDX :id and :start index of the given
   regex in the string if a match occurred, or nil if there was no match."
  [s elem]
  (when-let [match (rencg/re-find-ncg (:regex elem) s)]
    {:id    ((:fn elem) (merge {:name s} elem match))
     :start (:start match)}))

(defn- match-regexes
  "Returns a sequence (NOT A SET!) of the matched SPDX license or
  exception ids for the given string, or nil if there were no matches.
  Results are in the order in which they appear in the string."
  [s]
  (some->> (seq (filter identity (pmap (partial match-regex s) license-name-matching)))
           (sort-by :start)
           (map :id)))

(defn- split-on-operators
  "Case insensitively splits a string based on license operators (and,
  or, with), but only if they're not also part of a license name (e.g.
  'Common Development and Distribution License', 'GNU General Public
  License version 2.0 or (at your option) any later version', etc.)."
  [s]
  (when-not (s/blank? s)
    (map #(if (keyword? %) % (s/trim %))
         (mapcat #(if (keyword? %) [%] (interpose :with (s/split % #"(?i)\b(with|w/)(?!\s+the\s+acknowledgment\s+clause\s+removed)")))
                 (mapcat #(if (keyword? %) [%] (interpose :or (s/split % #"(?i)\bor(?!\s+(later|lator|newer|lesser|library))\b")))
                         (interpose :and (s/split s #"(?i)\b(and|\&)(?!(\s+distribution))\b")))))))

;####TODO: MAKE THIS FUNCTION RETURN METADATA ABOUT :concluded VS :declared AS WELL AS SOURCE!!!!
(defn- string->ids
  "Converts the given String into a sequence (NOT A SET!) of SPDX
  identifier(s), each of which is a listed SPDX license or exception id
  if the value is recognised, or a lice-comb specific 'unlisted'
  LicenseRef if not.  This involves:
  1. Seeing if it's a listed license or exception id
  2. Looking up the value in the names in the SPDX license and exception
     lists
  3. If the value is a URI, performing URI matching with it
  4. Using regexes to attempt to identify the license(s) and/or
     exception(s)
  5. Returning a lice-comb specific 'unlisted' LicenseRef"
  [s]
  (when-not (s/blank? s)
    ; 1. Is it an SPDX license or exception id?
    (let [s (s/trim s)]
      (if-let [spdx-id (get @spdx-ids-d (s/lower-case s))]
        [spdx-id]
        ; 2. Is it an SPDX license or exception name?
        (if-let [name-match (listed-name->ids s)]
          [name-match]
          ; 3. If it's a URI, perform URI matching on it (this is to handle some dumb corner cases that do exist in the real world)
          (if-let [uri-matches (uri->ids s)]
            (vec uri-matches)
            ; 4. Attempt regex name matching
            (if-let [re-name-matches (match-regexes s)]
              re-name-matches
                ; 5. Give up and return a lice-comb "unlisted" LicenseRef
                [(name->unlisted s)])))))))

(defn- process-expression-element
  "Processes a single new element being added to l, and will combine it
  with earlier elements in l where appropriate."
  [l e]
  (if (keyword? e)
    (conj l e)
    (case (count (take-while keyword? l))
      0 (if (= (peek l) e) l (conj l e))
      1 (let [kw      (s/upper-case (name (first l)))
              prior   (second l)
              earlier (rest (rest l))]
          (if (nil? prior)
            (conj earlier e)
            (conj earlier (s/join " " [prior kw e]))))
      (let [earlier (drop-while keyword? l)]
        (conj earlier e)))))

(defn- build-spdx-expressions
  "Builds a set of SPDX expression(s) from the given list containing strings and keywords."
  [l]
  (let [l (drop-while keyword? l)]
    (loop [result '()
           f      (first l)
           r      (rest l)]
      (if f
        (recur (process-expression-element result f) (first r) (rest r))
        (some-> (seq (reverse (drop-while keyword? result)))
                set)))))

;####TODO: MAKE THIS FUNCTION RETURN METADATA ABOUT :concluded VS :declared AND SOURCE!!!!
(defn name->expressions
  "Attempts to determine the SPDX license expression(s) (a set of Strings)
  from the given 'license name' (a String), or nil if there aren't any.
  This involves:
  1. Determining whether the name is a valid SPDX license expression, and if so
     normalising (see clj-spdx's spdx.expressions/normalise fn) and returning it
  2. constructing one or more SPDX license expressions by "
  [name]
  (when-not (s/blank? name)
    (let [name (s/trim name)]
      ; 1. If it's a valid SPDX expression, return the normalised rendition of it in a set
      (if-let [normalised-expression (sexp/normalise name)]
        #{normalised-expression}
        ; 2. Attempt to build SPDX expression(s) from the name
        (some->> (split-on-operators name)
                 (mapcat #(if (keyword? %) [%] (string->ids %)))
                 (map #(if (and (coll? %) (= 1 (count %))) (first %) %))
                 build-spdx-expressions)))))

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
          (string->ids name))))))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it.

  Note: this method has a substantial performance cost."
  []
  ; Parallelise initialisation of the license and exception lists, as they're both sloooooooow
  (future
    (sl/init!)
    @license-list-d)
  (future
    (se/init!)
    @exception-list-d)
  @spdx-ids-d
  @license-ids-for-matching-d
  @index-uri-to-id-d
  @index-name-to-id-d
  @http-client-d
  nil)
