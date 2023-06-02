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

(ns lice-comb.spdx
  "SPDX related functionality that isn't already provided by https://github.com/pmonks/clj-spdx"
  (:require [clojure.string        :as s]
            [clojure.set           :as set]
            [clojure.java.io       :as io]
            [clojure.reflect       :as cr]
            [clojure.edn           :as edn]
            [clojure.tools.logging :as log]
            [spdx.licenses         :as sl]
            [spdx.exceptions       :as se]
            [spdx.matching         :as sm]
            [lice-comb.data        :as lcd]
            [lice-comb.utils       :as lcu]))

; The lists
(def ^:private license-list-d   (delay (map sl/id->info (sl/ids))))
(def ^:private exception-list-d (delay (map sl/id->info (sl/ids))))

; License name aliases
(def ^:private aliases-uri (lcd/uri-for-data "/spdx/aliases.edn"))    ; ####TODO: UPGRADE THIS TO USE LicenseRef-lice-comb-public-domain INSTEAD OF NON-SPDX-Public-Domain
(def ^:private aliases-d   (delay
                             (try
                               (edn/read-string (slurp aliases-uri))
                               (catch Exception e
                                 (throw (ex-info (str "Unexpected " (cr/typename (type e)) " while reading " aliases-uri ". Please check your internet connection and try again.") {} e))))))

(defn- name->license-ids
  "Returns the SPDX license identifier(s) (a set) for the given license name
  (matched case insensitively), or nil if there aren't any.

  Note that SPDX license names are not guaranteed to be unique - see https://github.com/spdx/license-list-XML/blob/main/DOCS/license-fields.md"
  [name]
  (when-not (s/blank? name)
    (let [lname (s/trim (s/lower-case name))]
      (some-> (seq (map :id (filter #(= lname (s/trim (s/lower-case (:name %)))) @license-list-d)))
              set))))

(defn fuzzy-match-uri->license-ids
  "Returns the SPDX license identifiers (a set) for the given uri, or nil if
  there aren't any.

  Notes:
  1. this does not perform exact matching; rather it simplifies URIs in various
     ways to avoid irrelevant differences, including performing a
     case-insensitive comparison, ignoring protocol differences (http vs https),
     ignoring extensions representing MIME types (.txt vs .html, etc.), etc.
  2. SPDX license list URIs are not guaranteed to be unique"
  [uri]
  (when-not (s/blank? uri)
    (let [suri (lcu/simplify-uri uri)]
      (some-> (seq (map :id (filter #(some identity (map (fn [see-also] (s/starts-with? suri see-also)) (distinct (map lcu/simplify-uri (get-in % [:see-also :url])))))
                                    @license-list-d)))
              set))))

(defn id->name
  "Returns the name of the given license or exception identifier; either the
  official SPDX license or exception name or (if the id is not a listed SPDX id
  but is used by the library) an unofficial name. Returns the id as-is if unable
  to determine a name."
  [id]
  (cond (sl/listed-id? id)                                         (:name (sl/id->info id))
        (se/listed-id? id)                                         (:name (se/id->info id))
        (= (s/lower-case id) "licenseref-lice-comb-public-domain") "Public domain"
        :else                                                      id))


; Index of alias regexes
(def ^:private idx-regex-to-id-d (delay
                                   (merge @aliases-d
                                          (apply merge (map #(hash-map (s/replace (lcu/escape-re (s/lower-case (:name %))) #"\s+" "\\\\s+") #{(:id %)}) @license-list-d)))))

; Store regexes in reverse size order, on the assumption that longer regexes are more specific and should be processed first
; Note: `regexes` actually contains string representations, since regexes in Clojure don't implement equality / hash 🙄
(def ^:private regexes-d       (delay (reverse (sort-by #(count %) (concat (keys @idx-regex-to-id-d) (keys @idx-regex-to-id-d))))))
(def ^:private re-pattern-mem  (memoize re-pattern))   ; So we memomize re-pattern to save having to recompile the regex string representations every time we use them

(defn fuzzy-match-name->license-ids
  "Fuzzily attempts to determine the SPDX license identifier(s) (a set) from the
  given name (a string), or nil if there aren't any.  This involves three steps:
  1. checking if the name is actually an id (this is rare, but sometimes appears
     in pom.xml files)
  2. looking up the name using name->license-ids
  3. falling back on a manually maintained list of common name aliases: https://github.com/pmonks/lice-comb/blob/data/spdx/aliases.edn"
  [name]
  (when-not (s/blank? name)
    (let [name (s/trim name)]
      (if-let [list-id-match (sl/id->info name)]   ; First we exact match on the id, for those (rare) cases where someone has used an SPDX license id as the name (e.g. in a pom.xml file)
        #{(:id list-id-match)}
        (if-let [list-name-matches (name->license-ids name)]   ; Then we look up by name
          list-name-matches
          (if-let [re-name-matches (get @idx-regex-to-id-d (first (filter #(re-find (re-pattern-mem %) (s/lower-case name)) @regexes-d)))]   ; Then the last resort is to match on the regexes
            re-name-matches
            (log/warn "Unable to find a license for" (str "'" name "'"))))))))

(defmulti text->ids
  "Attempts to determine the SPDX license and/or exception identifier(s) (a set)
  within the given license text (a String, Reader, InputStream, or something
  that is accepted by clojure.java.io/reader - File, URL, URI, Socket, etc.).

  Notes:
  * the caller is expected to close a Reader or InputStream passed to this
    function (e.g. using clojure.core/with-open)
  * you cannot pass a String representation of a filename to this method - you
    should pass filenames to clojure.java.io/file first"
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
  (text->ids (slurp r)))

(defmethod text->ids java.io.InputStream
  [is]
  (text->ids (io/reader is)))

(defmethod text->ids :default
  [src]
  (when src
    (with-open [r (io/reader src)]
      (text->ids r))))

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
  @aliases-d
  @idx-regex-to-id-d
  @regexes-d
  nil)
