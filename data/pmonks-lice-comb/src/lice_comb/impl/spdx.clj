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

(ns lice-comb.impl.spdx
  "SPDX-related functionality. Note: this namespace is not part of the public
  API of lice-comb and may change without notice."
  (:require [clojure.string       :as s]
            [spdx.licenses        :as sl]
            [spdx.exceptions      :as se]
            [spdx.expressions     :as sexp]
            [lice-comb.impl.utils :as lciu]))

; The subset of SPDX license identifiers that we use; specifically excludes the superceded deprecated GPL family identifiers
(def license-ids-d
  (delay
    (disj (set (filter #(not (s/ends-with? % "+")) (sl/ids)))
          "AGPL-1.0" "AGPL-3.0" "GPL-1.0" "GPL-2.0" "GPL-3.0" "LGPL-2.0" "LGPL-2.1" "LGPL-3.0"
          "GPL-2.0-with-autoconf-exception" "GPL-2.0-with-bison-exception" "GPL-2.0-with-classpath-exception"
          "GPL-2.0-with-font-exception" "GPL-2.0-with-GCC-exception" "GPL-3.0-with-autoconf-exception"
          "GPL-3.0-with-GCC-exception")))

; The subset of SPDX exception identifiers that we use; right now this is all of them (placeholder in case we need to use a subset in future)
(def exception-ids-d (delay (se/ids)))

; The license and exception lists
(def license-list-d   (delay (map sl/id->info @license-ids-d)))
(def exception-list-d (delay (map se/id->info @exception-ids-d)))

; The license refs lice-comb uses (note: the unidentified one usually has a hyphen then a base62 suffix appended)
(def ^:private lice-comb-license-ref-prefix       "LicenseRef-lice-comb")
(def ^:private public-domain-license-ref          (str lice-comb-license-ref-prefix "-PUBLIC-DOMAIN"))
(def ^:private proprietary-commercial-license-ref (str lice-comb-license-ref-prefix "-PROPRIETARY-COMMERCIAL"))
(def ^:private unidentified-license-ref-prefix    (str lice-comb-license-ref-prefix "-UNIDENTIFIED"))

; The addition refs lice-comb uses (note: the unidentified one usually has a hyphen then a base62 suffix appended)
(def ^:private lice-comb-addition-ref-prefix      "AdditionRef-lice-comb")
(def ^:private unidentified-addition-ref-prefix   (str lice-comb-addition-ref-prefix "-UNIDENTIFIED"))

; Lower case id map
(def spdx-ids-d (delay (merge (into {} (map #(vec [(s/lower-case %) %]) @license-ids-d))
                              (into {} (map #(vec [(s/lower-case %) %]) @exception-ids-d)))))

(defn- name-to-id-tuple
  [list-entry]
  [(s/lower-case (s/trim (:name list-entry))) (:id list-entry)])

(def index-name-to-id-d (delay (merge (lciu/mapfonv #(lciu/nset (map second %)) (group-by first (map name-to-id-tuple @license-list-d)))
                                      (lciu/mapfonv #(lciu/nset (map second %)) (group-by first (map name-to-id-tuple @exception-list-d))))))

(defn- urls-to-id-tuples
  "Extracts all urls for a given list (license or exception) entry."
  [list-entry]
  (let [id              (:id list-entry)
        simplified-uris (map lciu/simplify-uri (filter (complement s/blank?) (concat (:see-also list-entry) (get-in list-entry [:cross-refs :url]))))]
    (map #(vec [% id]) simplified-uris)))

(def index-uri-to-id-d (delay (merge (lciu/mapfonv #(lciu/nset (map second %)) (group-by first (mapcat urls-to-id-tuples @license-list-d)))
                                     (lciu/mapfonv #(lciu/nset (map second %)) (group-by first (mapcat urls-to-id-tuples @exception-list-d))))))

(defn lice-comb-license-ref?
  "Is the given id one of lice-comb's custom LicenseRefs?"
  [id]
  (s/starts-with? (s/lower-case id) (s/lower-case lice-comb-license-ref-prefix)))

(defn lice-comb-addition-ref?
  "Is the given id one of lice-comb's custom AdditionRefs?"
  [id]
  (s/starts-with? (s/lower-case id) (s/lower-case lice-comb-addition-ref-prefix)))

(defn public-domain?
  "Is the given id lice-comb's custom 'public domain' LicenseRef?"
  [id]
  (= (s/lower-case id) (s/lower-case public-domain-license-ref)))

(def ^{:doc "Constructs a valid SPDX id (a LicenseRef specific to lice-comb)
  representing public domain."
       :arglists '([])}
  public-domain
  (constantly public-domain-license-ref))

(defn proprietary-commercial?
  "Is the given id lice-comb's custom 'proprietary / commercial' LicenseRef?"
  [id]
  (when id
    (= (s/lower-case id) (s/lower-case proprietary-commercial-license-ref))))

(def ^{:doc "Constructs a valid SPDX id (a LicenseRef specific to lice-comb)
  representing a proprietary / commercial license."
       :arglists '([])}
  proprietary-commercial
  (constantly proprietary-commercial-license-ref))

(defn unidentified-license-ref?
  "Is the given id a lice-comb custom 'unidentified' LicenseRef?"
  [id]
  (when id
    (s/starts-with? (s/lower-case id) (s/lower-case unidentified-license-ref-prefix))))

(defn unidentified-addition-ref?
  "Is the given id a lice-comb custom 'unidentified' AdditionRef?"
  [id]
  (when id
    (s/starts-with? (s/lower-case id) (s/lower-case unidentified-addition-ref-prefix))))

(defn unidentified?
  "Is the given id a lice-comb custom 'unidentified' LicenseRef or AdditionRef?"
  [id]
  (or (unidentified-license-ref? id) (unidentified-addition-ref? id)))

(defn name->unidentified-license-ref
  "Constructs a valid SPDX id (a LicenseRef specific to lice-comb) for an
  unidentified license, with the given name (if provided) appended as Base62
  (since clj-spdx identifiers are limited to a small superset of Base62)."
  ([] (name->unidentified-license-ref nil))
  ([name]
   (str unidentified-license-ref-prefix (when-not (s/blank? name) (str "-" (lciu/base62-encode name))))))

(defn name->unidentified-addition-ref
  "Constructs a valid SPDX id (an AdditionRef specific to lice-comb) for an
  unidentified license exception, with the given name (if provided) appended as
  Base62 (since clj-spdx identifiers are limited to a small superset of Base62)."
  ([] (name->unidentified-addition-ref nil))
  ([name]
   (str unidentified-addition-ref-prefix (when-not (s/blank? name) (str "-" (lciu/base62-encode name))))))

(defn unidentified-license-ref->name
  "Get the original name of the given unidentified license ref. Returns nil if
  id is nil or is not a lice-comb unidentified LicenseRef."
  [id]
  (when (unidentified-license-ref? id)
    (if (> (count id) (count unidentified-license-ref-prefix))
      (lciu/base62-decode (subs id (inc (count unidentified-license-ref-prefix))))
      "")))

(defn unidentified-addition-ref->name
  "Get the original name of the given unidentified addition ref. Returns nil if
  id is nil or is not a lice-comb unidentified AdditionRef."
  [id]
  (when (unidentified-addition-ref? id)
    (if (> (count id) (count unidentified-license-ref-prefix))
      (lciu/base62-decode (subs id (inc (count unidentified-license-ref-prefix))))
      "")))

(defn unidentified->name
  "Get the original name of the given unidentified license ref or addition ref.
  Returns nil if id is nil or is not a lice-comb unidentified LicenseRef or
  AdditionRef."
  [id]
  (cond
    (unidentified-license-ref?  id) (unidentified-license-ref->name id)
    (unidentified-addition-ref? id) (unidentified-addition-ref->name id)))

(defn unidentified-license-ref->human-readable-name
  "Returns the string 'Unidentified' with the original name of the given
  unidentified license in parens. Returns nil if id is nil or is not a
  lice-comb unidentified LicenseRef."
  [id]
  (when (unidentified-license-ref? id)
    (let [original-name (unidentified->name id)]
      (str "Unidentified (\""
           (if (s/blank? original-name)
             "-original name not available-"
             (s/trim original-name))
           "\")"))))

(defn unidentified-addition-ref->human-readable-name
  "Returns the string 'Unidentified' with the original name of the given
  unidentified license exception in parens. Returns nil if id is nil or
  is not a lice-comb unidentified AdditionRef."
  [id]
  (when (unidentified-addition-ref? id)
    (let [original-name (unidentified->name id)]
      (str "Unidentified (\""
           (if (s/blank? original-name)
             "-original name not available-"
             (s/trim original-name))
           "\")"))))

(defn unidentified->human-readable-name
  "Returns the string 'Unidentified' with the original name of the given
  unidentified license or license exception in parens. Returns nil if id is nil
  or is not a lice-comb unidentified LicenseRef or AdditionRef."
  [id]
  (cond
    (unidentified-license-ref?  id) (unidentified-license-ref->human-readable-name id)
    (unidentified-addition-ref? id) (unidentified-addition-ref->human-readable-name id)))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it.

  Note: this method has a substantial performance cost."
  []
  ; Parallelise initialisation of the spdx.licenses and spdx.exceptions namespaces, as they're both sloooooooow (~1.5 mins total)
  (let [sl-init (future (sl/init!))
        se-init (future (se/init!))]
    @sl-init
    @se-init)
  (sexp/init!)

  ; Serially initialise this namespace's dependent state - they're all pretty fast (< 1s)
  @license-ids-d
  @exception-ids-d
  @license-list-d
  @exception-list-d
  @spdx-ids-d
  @index-uri-to-id-d
  @index-name-to-id-d
  nil)
