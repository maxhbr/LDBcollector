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

(ns lice-comb.impl.parsing
  "License name, URI, and text parsing functionality. Note: this namespace is
  not part of the public API of lice-comb and may change without notice."
  (:require [clojure.string                  :as s]
            [clojure.set                     :as set]
            [clojure.java.io                 :as io]
            [spdx.licenses                   :as sl]
            [spdx.exceptions                 :as se]
            [spdx.matching                   :as sm]
            [spdx.expressions                :as sexp]
            [embroidery.api                  :as e]
            [lice-comb.impl.spdx             :as lcis]
            [lice-comb.impl.id-detection     :as lciid]
            [lice-comb.impl.splitting        :as lcisp]
            [lice-comb.impl.expressions-info :as lciei]
            [lice-comb.impl.http             :as lcihttp]
            [lice-comb.impl.data             :as lcid]
            [lice-comb.impl.utils            :as lciu]))

(def ^:private cursed-names-d (delay (lcid/load-edn-resource "lice_comb/names.edn")))

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
  "If the keys of expressions includes both an 'only' and an 'or-later' variant
  of the same underlying GNU family identifier, remove the 'only' variant."
  [expressions]
  (loop [result expressions
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
  "If the keys of expressions includes both CC0-1.0 and lice-comb's public
  domain LicenseRef, remove the LicenseRef as it's redundant."
  [expressions]
  (if (and (contains? expressions (lcis/public-domain))
           (contains? expressions "CC0-1.0"))
    (dis expressions (lcis/public-domain))
    expressions))

(defn- fix-mpl-2
  "If the keys of expressions includes both MPL-2.0 and
  MPL-2.0-no-copyleft-exception, remove MPL-2.0-no-copyleft-exception as it's
  redundant."
  [expressions]
  (if (and (contains? expressions "MPL-2.0")
           (contains? expressions "MPL-2.0-no-copyleft-exception"))
    (dis expressions "MPL-2.0-no-copyleft-exception")
    expressions))

(defn- fix-license-id-with-exception-id
  "Combines instances where there are two keys, one of them a license identifier
  and the other an exception identifier."
  [expressions]
  (if (= 2 (count expressions))
    (if (set? expressions)
      ; expressions is a set
      (let [license-id   (first (seq (filter #(or (sl/listed-id? %) (sl/license-ref?  %)) expressions)))
            exception-id (first (seq (filter #(or (se/listed-id? %) (se/addition-ref? %)) expressions)))]
        (if (and license-id exception-id)
          #{(str license-id " WITH " exception-id)}
          expressions))
      ; expressions is a map
      (let [exprs        (keys expressions)
            license-id   (first (seq (filter #(or (sl/listed-id? %) (sl/license-ref?  %)) exprs)))
            exception-id (first (seq (filter #(or (se/listed-id? %) (se/addition-ref? %)) exprs)))]
        (if (and license-id exception-id)
          {(str license-id " WITH " exception-id) (reduce concat (vals expressions))}
          expressions)))
    expressions))

(defn manual-fixes
  "Manually fix certain invalid combinations of license identifiers in a set or
  map of expressions."
  [expressions]
  (some-> expressions
          fix-gpl-only-or-later
          fix-public-domain-cc0
          fix-mpl-2
          fix-license-id-with-exception-id))

(defmulti match-text
  "Returns an expressions-info map for the given license text, or nil if no
  matches are found."
  {:arglists '([text])}
  class)

(defmethod match-text java.lang.String
  [s]
  ; clj-spdx's *-within-text APIs are *expensive* but support batching, so we check batches of ids in parallel
  (let [num-cpus             (.availableProcessors (Runtime/getRuntime))
        license-id-batches   (partition num-cpus @lcis/license-ids-d)
        exception-id-batches (partition num-cpus @lcis/exception-ids-d)
        license-ids-found    (apply set/union (e/pmap* #(sm/licenses-within-text   s %) license-id-batches))
        exception-ids-found  (apply set/union (e/pmap* #(sm/exceptions-within-text s %) exception-id-batches))
        expressions-found    (if (and (= 1 (count license-ids-found))
                                      (= 1 (count exception-ids-found)))
                               #{(str (first license-ids-found) " WITH " (first exception-ids-found))}
                               (set/union license-ids-found exception-ids-found))]
    (when expressions-found
      ; Note: we don't need to sexp/normalise the keys here, as the only expressions that can be returned are constructed correctly
      (manual-fixes (into {} (map #(hash-map % (list {:id % :type :concluded :confidence :high :strategy :spdx-matching-guidelines})) expressions-found))))))

(defmethod match-text java.io.Reader
  [r]
  (let [sw (java.io.StringWriter.)]
    (io/copy r sw)
    (match-text (str sw))))

(defmethod match-text java.io.InputStream
  [is]
  (match-text (io/reader is)))

(defmethod match-text :default
  [src]
  (when src
    (with-open [r (io/reader src)]
      (doall (match-text r)))))

(defn parse-uri
  "Parses the given license `uri`, returning an expressions-info map, or `nil`
  if no matching license ids were found."
  [uri]
  (when-not (s/blank? uri)
    (let [result (manual-fixes
                   (or
                     ; 1. Is the URI a close match for any of the URIs in the SPDX license or exception lists?
                     (when-let [ids (lcis/near-match-uri uri)]
                       (into {} (map #(hash-map % (list {:id % :type :concluded :confidence :high :strategy :spdx-listed-uri :source (list uri)})) ids)))

                     ; 2. attempt to retrieve the text/plain contents of the uri and perform license text matching on it
                     (when-let [license-text (lcihttp/get-text uri)]
                       (match-text license-text))))]
      ; We don't need to sexp/normalise the keys here, as we never detect an expression from a URI
      (lciei/prepend-source uri result))))

(defn- string->ids-info
  "Converts the given string (a fragment of a license name) into a **sequence**
  of singleton expressions-info maps (one per expression), ordered in the same
  order of appearance as they appear in s.

  If no listed SPDX license or exception identifiers are found in s, returns a
  sequence containing a single expressions-info map with a String started with
  \"UNIDENTIFIED-\" and with s appended. Callers are expected to turn this value
  into a lice-comb unidentified LicenseRef or AdditionRef, depending on context."
  [s]
  (when-not (s/blank? s)
    (let [s   (s/trim s)
          ids (or
                ; 1. Is it cursed?
                (when-let [cursed-name (get @cursed-names-d s)]
                  (map #(apply hash-map %) cursed-name))

                ; 2. Is it an SPDX license or exception id?
                (when-let [id (lcis/near-match-id s)]
                  (if (= id s)
                    (list {id (list {:id id :type :declared :strategy :spdx-listed-identifier-exact-match :source (list s)})})
                    (list {id (list {:id id :type :concluded :confidence :high :strategy :spdx-listed-identifier-case-insensitive-match :source (list s)})})))

                ; 3. Is it the name of one or more SPDX licenses or exceptions?
                (when-let [ids (lcis/near-match-name s)]
                  (map #(hash-map % (list {:id % :type :concluded :confidence :high :strategy :spdx-listed-name :source (list s)})) ids))

                ; 4. Might it be a URI?  (this is to handle some dumb corner cases that exist in pom.xml files hosted on Clojars & Maven Central)
                (when-let [ids (parse-uri s)]
                  (map #(hash-map (key %) (val %)) ids))

                ; 5. Attempt to detect ids in the string
                (lciid/detect-ids s)

                ; 6. No clue, so return a single info map, but with a made up "UNIDENTIFIED-" value (NOT A LICENSEREF!) instead of an SPDX license or exception identifier
                (let [id (str "UNIDENTIFIED-" s)]
                  (list {id (list {:id id :type :concluded :confidence :low :confidence-explanations [:unidentified] :strategy :unidentified :source (list s)})})))]
      (map (partial lciei/prepend-source s) ids))))

(defn- fix-unidentified
  "Fixes a singleton UNIDENTIFIED- expression info map by converting the id to
  either a lice-comb unidentified LicenseRef or AdditionRef, depending on prev.
  Returns x unchanged if it's neither an expression info map nor has an
  UNIDENTIFIED- id."
  ([x] (fix-unidentified nil x))
  ([prev x]
   (if-not (map? x)
     ; It's not an expression info map (i.e. it's an operator keyword), so let it through unchanged
     x
     ; It's a (singleton) expression info map 
     (let [id (first (keys x))]
       (if (s/starts-with? id "UNIDENTIFIED-")
         ; It's an expression info map with an unidentified id, so we have to fix it
         (let [fixed-id  (if (= :with prev)
                           (lcis/name->unidentified-addition-ref (subs id (count "UNIDENTIFIED-")))
                           (lcis/name->unidentified-license-ref  (subs id (count "UNIDENTIFIED-"))))
               v         (first (vals x))
               fixed-val (map #(if (:id %) (assoc % :id fixed-id) %) v)]
          {fixed-id fixed-val})
         ; It's a (singleton) expression info map but with an identified id, so let it through unchanged
         x)))))

(defn- fix-unidentifieds
  "Fixes all entries in sequence l that have an UNIDENTIFIED- id by converting
  those ids to either a lice-comb unidentified LicenseRef or AdditionRef,
  depending on context (i.e. whether the entry is preceeded by a :with operator
  or not)."
  [l]
  (loop [f      (take 2 l)
         r      (rest l)
         result (list (fix-unidentified (first f)))]
    (if-not (seq f)
      result
      (recur (take 2 r)
             (rest r)
             (if-let [fixed-id-with-info (fix-unidentified (first f) (second f))]
               (concat result [fixed-id-with-info])
               result)))))

(def ^:private push conj)   ; With lists-as-stacks conj == push

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
            (if (or (not= :with kw)  ; If the prior keyword was :and or :or, or :with and the current element is a listed exception id or AdditionRef, build an SPDX expression fragment and push the result onto s
                    (se/listed-id?    (first (keys e)))
                    (se/addition-ref? (first (keys e))))
              (let [k                (s/join " " [(first (keys prior)) operator (first (keys e))])
                    expression-infos (concat (first (vals prior)) (first (vals e)))
                    v                (distinct (concat (list {:type :concluded :confidence (lciei/calculate-confidence-for-expression expression-infos) :strategy :expression-inference})
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

(defn parse-name
  "Parses the given license `n`ame, returning an expressions-info map."
  [n]
  (when-not (s/blank? n)
    (let [n              (s/trim n)
          partial-result (some->> n
                                  lcisp/split-on-operators                         ; Split on operators
                                  (map #(if (keyword? %) % (string->ids-info %)))  ; Determine SPDX ids (or UNIDENTIFIED-xxx) with info for all non-operators
                                  flatten                                          ; Flatten back to an unnested sequence (since string->ids-info returns sequences)
                                  fix-unidentifieds                                ; Convert each unidentified non-operator into either a LicenseRef or AdditionRef, depending on context
                                  seq)
          ids-only       (seq (mapcat keys (filter map? partial-result)))
          result         ; Check whether all we have are unidentified LicenseRefs/AdditionRefs, and if so just return the entire thing as a single unidentified LicenseRef
                         (if (every? lcis/unidentified? ids-only)
                           (let [id (lcis/name->unidentified-license-ref n)]
                             {id (list {:id id :type :concluded :confidence :low :confidence-explanations [:unidentified] :strategy :unidentified :source (list)})})
                           (some->> partial-result
                                    build-expressions-info-map
                                    (lciu/mapfonk sexp/normalise)))]
      (lciei/prepend-source n result))))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it.

  Note: this method has a substantial performance cost."
  []
  (lcis/init!)
  (lciid/init!)
  (lcihttp/init!)
  @cursed-names-d
  nil)
