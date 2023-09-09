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
  (:require [clojure.string                  :as s]
            [clojure.set                     :as set]
            [clojure.java.io                 :as io]
            [spdx.exceptions                 :as se]
            [spdx.matching                   :as sm]
            [lice-comb.impl.spdx             :as lcis]
            [lice-comb.impl.regex-matching   :as lcirm]
            [lice-comb.impl.expressions-info :as lciei]
            [lice-comb.impl.3rd-party        :as lc3]
            [lice-comb.impl.http             :as lcihttp]
            [lice-comb.impl.data             :as lcid]
            [lice-comb.impl.utils            :as lciu]))

(def ^:private cursed-names-d (delay (lcid/load-edn-resource "lice_comb/names.edn")))

(def ^:private direct-replacements-map {
  #{"GPL-2.0-only"     "Classpath-exception-2.0"} #{"GPL-2.0-only WITH Classpath-exception-2.0"}
  #{"GPL-2.0-or-later" "Classpath-exception-2.0"} #{"GPL-2.0-or-later WITH Classpath-exception-2.0"}
  #{"GPL-3.0-only"     "Classpath-exception-2.0"} #{"GPL-3.0-only WITH Classpath-exception-2.0"}
  #{"GPL-3.0-or-later" "Classpath-exception-2.0"} #{"GPL-3.0-or-later WITH Classpath-exception-2.0"}
  })

(defn- direct-replacements
  "Self-evident direct replacements."
  [ids]
  (get direct-replacements-map ids ids))

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

(defn- dis
  "Remove the given key(s) from the associative collection (set or map)."
  [associative & ks]
  (cond (set? associative) (apply disj   associative ks)
        (map? associative) (apply dissoc associative ks)))

(defn- fix-gpl-only-or-later
  "If the keys of ids includes both an 'only' and an 'or-later' variant of the
  same underlying GNU family identifier, remove the 'only' variant."
  [ids]
  (loop [result ids
         f      (first gpl-ids-with-only-or-later)
         r      (rest  gpl-ids-with-only-or-later)]
    (if f
      (recur (if (and (contains? result (str f "-only"))
                      (contains? result (str f "-or-later")))
               (dis result (str f "-only"))
               result)
             (first r)
             (rest r))
      result)))

(defn- fix-public-domain-cc0
  "If the keys of ids includes both CC0-1.0 and lice-comb's public domain
  LicenseRef, remove the LicenseRef as it's redundant."
  [ids]
  (if (and (contains? ids (lcis/public-domain))
           (contains? ids "CC0-1.0"))
    (dis ids (lcis/public-domain))
    ids))

(defn- fix-mpl-2
  "If the keys of ids includes both MPL-2.0 and MPL-2.0-no-copyleft-exception,
  remove the MPL-2.0-no-copyleft-exception as it's redundant."
  [ids]
  (if (and (contains? ids "MPL-2.0")
           (contains? ids "MPL-2.0-no-copyleft-exception"))
    (dis ids "MPL-2.0-no-copyleft-exception")
    ids))

(defn manual-fixes
  "Manually fix certain invalid combinations of license identifiers in a set or
  map."
  [ids]
  (some-> ids
          direct-replacements
          fix-gpl-only-or-later
          fix-public-domain-cc0
          fix-mpl-2))

(defmulti text->ids
  "Returns an expressions-map for the given license text, or nil if no matches
  are found."
  {:arglists '([text])}
  type)

(defmethod text->ids java.lang.String
  [s]
  ; These clj-spdx APIs are *expensive*, so we paralellise them
  (let [f-lic    (future (sm/licenses-within-text   s @lcis/license-ids-d))
        f-exc    (future (sm/exceptions-within-text s @lcis/exception-ids-d))
        ids      (set/union @f-lic @f-exc)]
    (when ids
      (manual-fixes (into {} (map #(hash-map % (list {:id % :type :concluded :confidence :high :strategy :spdx-text-matching})) ids))))))

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

(defn uri->ids
  "Returns an expressions-map for the given license uri, or nil if no matches
  are found."
  [uri]
  (when-not (s/blank? uri)
    (lciei/prepend-source uri
                          (manual-fixes
                            (let [suri (lciu/simplify-uri uri)]
                              (or ; 1. Does the simplified URI match any of the simplified URIs in the SPDX license or exception lists?
                                (when-let [ids (get @lcis/index-uri-to-id-d suri)]
                                  (into {} (map #(hash-map % (list {:id % :type :concluded :confidence :high :strategy :spdx-listed-uri :source (list uri)})) ids)))

                                ; 2. attempt to retrieve the text/plain contents of the uri and perform license text matching on it
                                (when-let [license-text (lcihttp/get-text uri)]
                                  (when-let [ids (text->ids license-text)]
                                    ids))))))))

(defn- string->ids-info
  "Converts the given string (a fragment of a license name) into a sequence of
  singleton expressions-info maps (one per expression), ordered in the same
  order of appearance as they appear in s.

  If no listed SPDX license or exception identifiers are found in s, returns a
  sequence containing a single expressions-info map with a lice-comb specific
  'unlisted' LicenseRef that encodes s."
  [s]
  (when-not (s/blank? s)
    (let [s   (s/trim s)
          ids (or ; 1. Is it an SPDX license or exception id?
                (when-let [id (get @lcis/spdx-ids-d (s/lower-case s))]
                  (if (= id s)
                    (list {id (list {:id id :type :declared :strategy :spdx-listed-identifier-exact-match :source (list s)})})
                    (list {id (list {:id id :type :concluded :confidence :high :strategy :spdx-listed-identifier-case-insensitive-match :source (list s)})})))

                ; 2. Is it the name of one or more SPDX licenses or exceptions?
                (when-let [ids (get @lcis/index-name-to-id-d (s/lower-case s))]
                  (map #(hash-map % (list {:id % :type :concluded :confidence :high :strategy :spdx-listed-name :source (list s)})) ids))

                ; 3. Might it be a URI?  (this is to handle some dumb corner cases that exist in pom.xml files hosted on Clojars & Maven Central)
                (when-let [ids (uri->ids s)]
                  (map #(hash-map (key %) (val %)) ids))

                ; 4. Attempt regex name matching
                (lcirm/matches s)

                ; 5. No clue, so return a single unlisted SPDX LicenseRef
                (let [id (lcis/name->unlisted s)]
                  (list {id (list {:id id :type :concluded :confidence :low :strategy :unlisted :source (list s)})})))]
      (map (partial lciei/prepend-source s) ids))))

(defn- filter-blanks
  "Filter blank strings out of coll"
  [coll]
  (when (seq coll)
    (seq (filter #(or (not (string? %)) (not (s/blank? %))) coll))))

(defn- map-split-and-interpose
  "Maps over the given sequence, splitting strings using the given regex re and
  interposing the given value int, returning a (flattened) sequence."
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
         (map-split-and-interpose #"(?i)(\band\b|\&)(?!\s+(distribution|all\s+rights\s+reserved))"                                                                :and)
         (map-split-and-interpose #"(?i)\bor\b(?!\s*(-?later|lator|newer|lesser|library|\(?at\s+your\s+(option|discretion)\)?|([\"']?(Revised|Modified)[\"']?)))" :or)
         (map-split-and-interpose #"(?i)\b(with\b|w/)(?!\s+the\s+acknowledgment\s+clause\s+removed)"                                                              :with)
         filter-blanks
         (map #(if (string? %) (s/trim %) %)))))

(def ^:private push conj)   ; With lists-as-stacks conj == push

(defn- calculate-confidence-for-expression
  "Calculate the confidence for an expression, as the lowest confidence in the
  expression-infos for the identifiers that make up the expression"
  [expression-infos]
  (if-let [confidence (lciei/lowest-confidence (filter identity (map :confidence expression-infos)))]
    confidence
    :high))   ; For when none of the components have a confidence (i.e. they're all :type :declared)

(defn- process-expression-element
  "Processes a single new expression element e (either a keyword representing
  an SPDX operator, or a map representing an SPDX identifier) in the context of
  stack (list) s."
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
                    (se/listed-id? (first (keys e))))
              (let [k                (s/join " " [(first (keys prior)) operator (first (keys e))])
                    expression-infos (concat (first (vals prior)) (first (vals e)))
                    v                (distinct (concat (list {:type :concluded :confidence (calculate-confidence-for-expression expression-infos) :strategy :expression-inference})
                                                       expression-infos))]
                (push s-minus-2 {k v}))
              (push s-minus-1 e))))  ; We had a :with operator without a valid exception id following it, so simply drop the :with keyword from the stack and push the current element on

      ; Many keywords? That's invalid (since we dedupe them when they get pushed on, so this means they're different), so drop all of them and push e onto s
      (push (drop-while keyword? s) e))))

(defn- build-expressions-info-map
  "Builds an expressions-info map from the given sequence of keywords and SPDX
  expression maps."
  [l]
  (loop [result '()
         f      (first l)
         r      (rest l)]
    (if f
      (recur (process-expression-element result f) (first r) (rest r))
      (manual-fixes (into {} result)))))

(defn name->expressions-info
  "Returns an expressions-info map for the given license name."
  [name]
  (when-not (s/blank? name)
    (let [name (s/trim name)]
      (lciei/prepend-source name
                            (or ; 1. Is it a cursed name?
                                (get @cursed-names-d name)

                                ; 2. Construct an expressions-info map from the name
                                (some->> (split-on-operators name)
                                         (drop-while keyword?)
                                         (lc3/rdrop-while keyword?)
                                         (map #(if (keyword? %) % (string->ids-info %)))
                                         flatten
                                         seq
                                         build-expressions-info-map))))))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it.

  Note: this method has a substantial performance cost."
  []
  (lcis/init!)
  (lcirm/init!)
  (lcihttp/init!)
  @cursed-names-d
  nil)
