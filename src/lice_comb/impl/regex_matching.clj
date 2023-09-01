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

(ns lice-comb.impl.regex-matching
  "Helper functionality focused on regex matching. Note: this namespace is not
  part of the public API of lice-comb and may change without notice."
  (:require [clojure.string       :as s]
            [rencg.api            :as rencg]
            [lice-comb.impl.spdx  :as lcis]
            [lice-comb.impl.utils :as lcu]))

(defn- get-rencgs
  "Get a value for an re-ncg, potentially looking at multiple ncgs in order
  until a non-blank value is found. Also trims and lower-cases the value, and
  replaces all whitespace with a single space."
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

(defn- assert-listed-id
  "Checks that the id is a listed SPDX identifier (license or exception) and
  throws if not. Returns the id."
  [id]
  (if (or (contains? @lcis/license-ids-d   id)
          (contains? @lcis/exception-ids-d id))
    id
    (throw (ex-info (str "Invalid SPDX id constructed: '" id
                         "'' - please raise an issue at "
                         "https://github.com/pmonks/lice-comb/issues/new?assignees=pmonks&labels=bug&template=Invalid_id_constructed.md&title=Invalid+SPDX+identifer+constructed:+" id)
                    {:id id}))))

(defn- generic-id-constructor
  "A generic SPDX id constructor which works for many simple regexes."
  [m]
  (when m
    (let [id (str (:id m)
               (when-let [ver (get-rencgs m ["version"] (:latest-ver m))]
                 (str "-"
                      ver
                      (when (and (:pad-ver? m)
                                 (not (s/includes? ver ".")))
                        ".0"))))]
      (assert-listed-id id))))

(defn- number-name-to-number
  "Converts the name of a number to that number (as a string). e.g.
  \"two\" -> \"2\".  Returns s unchanged if it's not a number name."
  [^String s]
  (when s
    (case s
      "two"   "2"
      "three" "3"
      "four"  "4"
      s)))

(defn- bsd-id-constructor
  "An SPDX id constructor specific to the BSD family of licenses."
  [m]
  (let [clause-count1          (number-name-to-number (get-rencgs m ["clausecount1"]))
        clause-count2          (number-name-to-number (get-rencgs m ["clausecount2"]))
        preferred-clause-count (case [(lcu/is-digits? clause-count1) (lcu/is-digits? clause-count2)]
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
    (if (contains? @lcis/license-ids-d id-with-suffix)  ; Not all suffixes are valid with all BSD clause counts, so check that it's valid before returning it
      id-with-suffix
      (assert-listed-id base-id))))

(defn- cc-id-constructor
  "An SPDX id constructor specific to the Creative Commons family of licenses."
  [m]
  (let [nc?     (not (s/blank? (get-rencgs m ["noncommercial"])))
        nd?     (not (s/blank? (get-rencgs m ["noderivatives"])))
        sa?     (not (s/blank? (get-rencgs m ["sharealike"])))
        version (let [ver (s/replace (get-rencgs m ["version"] (:latest-ver m)) #"\p{Punct}+" ".")]
                  (if (s/includes? ver ".")
                    ver
                    (str ver ".0")))
        base-id (str "CC-BY-"
                  (when nc?                 "NC-")
                  (when nd?                 "ND-")
                  (when (and (not nd?) sa?) "SA-")   ; SA and ND are incompatible (and have no SPDX id as a result), and if both are (erroneously) specified we conservatively choose ND
                  version)
        region  (case (get-rencgs m ["region"])
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
    (if (contains? @lcis/license-ids-d id-with-region)  ; Not all license variants and versions have a region specific identifier, so check that it's valid before returning it
      id-with-region
      (assert-listed-id base-id))))

(defn- gpl-id-constructor
  "An SPDX id constructor specific to the GNU family of licenses."
  [m]
  (let [variant (cond (contains? m "agpl") "AGPL"
                      (contains? m "lgpl") "LGPL"
                      (contains? m "gpl")  "GPL")
        version (let [ver (s/replace (get-rencgs m ["version"] (:latest-ver m)) #"\p{Punct}+" ".")]
                  (if (s/includes? ver ".")
                    ver
                    (str ver ".0")))
        suffix  (if (contains? m "orLater")
                  "or-later"
                  "only")  ; Note: we (conservatively) default to "only" when we don't have an explicit suffix
        id      (str variant "-" version  "-" suffix)]
    (assert-listed-id id)))

(defn- simple-regex-match
  "Constructs a 'simple' name match structure"
  [s]
  {:id    s
   :regex (re-pattern (str "(?i)\\b" s "\\b"))
   :fn    (constantly s)})

; The regex for the GNU family is a nightmare, so we build it up (and test it) in pieces
(def agpl-re          #"(?<agpl>AGPL|Affero)(\s+GNU)?(\s+General)?(\s+Public)?(\s+Licen[cs]e)?(\s+\(?AGPL\)?)?")
(def lgpl-re          #"(?<lgpl>L\s?GPL|GNU\s+(Library|Lesser)|(Library|Lesser)\s+(L?GPL|General\s+Public\s+Licen[cs]e))(\s+or\s+Lesser)?(\s+General)?(\s+Pub?lic)?(\s+Licen[cs]e)?(\s+\(?LGPL\)?)?")
(def gpl-re           #"(?<!(Affero|Lesser|Library)\s+)(?<gpl>GNU(?!\s+Classpath)|(?<!(L|A)\s*)GPL|General\s+Public\s+Licen[cs]e)(?!\s+(Affero|Library|Lesser|General\s+Lesser|General\s+Library|LGPL|AGPL))((\s+General)?(?!\s+(Affero|Lesser|Library))\s+Public\s+Licen[cs]e)?(\s+\(?GPL\)?)?")
(def version-re       #"[\s,-]*(_?V(ersion)?)?[\s\._]*(?<version>\d+([\._]\d+)?)?")
(def only-or-later-re #"[\s-]*((?<only>only)|(\(?or(\s+\(?at\s+your\s+(option|discretion)\)?)?(\s+any)?)?([\s-]*(?<orLater>later|lator|newer|\+)))?")
(def gnu-re           (lcu/re-concat "(?x)(?i)\\b(\n# Alternative 1: AGPL\n"
                                     agpl-re
                                     "\n# Alternative 2: LGPL\n|"
                                     lgpl-re
                                     "\n# Alternative 3: GPL\n|"
                                     gpl-re
                                     "\n)\n# Version\n"
                                     version-re
                                     "\n# Only/or-Later suffix\n"
                                     only-or-later-re))

; Regexes used for license name matching, along with functions for constructing an SPDX id from them
(def ^:private license-name-matching-d (delay
  (concat
    ; By default we add most SPDX ids as "simple" regex matches
    (map simple-regex-match (disj @lcis/license-ids-d "MIT" "Zlib"))
    (map simple-regex-match (disj @lcis/exception-ids-d "Classpath-exception-2.0"))
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
       :regex      #"(?i)(\bCC\sBY|Creative[\s-]+Commons(?!([\s-]+Legal[\s-]+Code)?[\s-]+Attribution)|(Creative[\s-]+Commons[\s-]+([\s-]+Legal[\s-]+Code)?)?(?<!BSD[\s-]+(\d|two|three|four)[\s-]+Clause\s+)Attribution)([\s,-]*((?<noncommercial>Non\s*Commercial|NC)|(?<noderivatives>No[\s-]*Deriv(ative)?s?|ND)|(?<sharealike>Share[\s-]*Alike|SA)))*(V(ersion)?)?\s*(?<version>\d+(\.\d+)?)?\s*(?<region>Australia|Austria|England((\s+and|\&)?\s+Wales)?|France|Germany|IGO|Japan|Netherlands|UK|United\s+States|USA?)?"
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
       :regex      gnu-re
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
      {:id         "MX4J"
       :regex      #"(?i)\bMX4J\s+Licen[cs]e(,?\s+v(ersion)?\s*1\.0)?\b"
       :fn         (constantly "Apache-1.1")}  ; See https://github.com/spdx/license-list-XML/pull/594 - the MX4J license *is* the Apache-1.1 license, according to SPDX
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
       :fn         lcis/proprietary-commercial}
      {:id         "Public Domain"
       :regex      #"(?i)\bPublic\s+Domain(?![\s\(]*CC\s*0)"
       :fn         lcis/public-domain}
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
      ])))

(defn- match-regex
  "Returns a map containing the SPDX :id and :start index of the given
   regex in the string if a match occurred, or nil if there was no match."
  [s elem]
  (when-let [match (rencg/re-find-ncg (:regex elem) s)]
    {:id    ((:fn elem) (merge {:name s} elem match))
     :start (:start match)}))

(defn match-regexes
  "Returns a sequence (NOT A SET!) of the matched SPDX license or
  exception ids for the given string, or nil if there were no matches.
  Results are in the order in which they appear in the string."
  [s]
  (some->> (seq (filter identity (pmap (partial match-regex s) @license-name-matching-d)))
           (sort-by :start)
           (map :id)
           distinct))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it.

  Note: this method has a substantial performance cost."
  []
  (lcis/init!)
  @license-name-matching-d
  nil)
