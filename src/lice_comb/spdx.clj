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
  "SPDX related functionality."
  (:require [clojure.string  :as s]
            [clojure.java.io :as io]
            [clojure.reflect :as cr]
            [clojure.edn     :as edn]
            [cheshire.core   :as json]
            [lice-comb.utils :as u]))

(def ^:private spdx-license-list-uri "https://spdx.org/licenses/licenses.json")
(def ^:private spdx-license-list     (try
                                       (json/parse-string (slurp spdx-license-list-uri) u/clojurise-json-key)
                                       (catch Exception e
                                         (throw (ex-info (str "Unexpected " (cr/typename (type e)) " while reading " spdx-license-list-uri ". Please check your internet connection and try again.") {})))))

(def ^:private aliases-uri (str (System/getProperty "user.home") "/Development/personal/lice-comb-data/spdx/aliases.edn"))   ; For testing changes locally
;(def ^:private aliases-uri "https://raw.githubusercontent.com/pmonks/lice-comb/data/spdx/aliases.edn")
(def ^:private aliases     (try
                             (edn/read-string (slurp aliases-uri))
                             (catch Exception e
                               (throw (ex-info (str "Unexpected " (cr/typename (type e)) " while reading " aliases-uri ". Please check your internet connection and try again.") {})))))

(def license-list-version
  "The version of the license list in use."
  (:license-list-version spdx-license-list))

(def license-list
  "The SPDX license list."
  (:licenses spdx-license-list))

; Alternative indexes into the SPDX list
(def ^:private idx-id-to-info  (into {} (map #(vec [(:license-id %) %]) license-list)))
(def ^:private idx-lname-to-id (apply merge (map #(hash-map (s/trim (s/lower-case (:name %))) (:license-id %)) license-list)))
(def ^:private idx-uri-to-id   (into {} (mapcat (fn [lic] (map #(vec [(u/simplify-uri %) (:license-id lic)]) (:see-also lic))) license-list)))
(def ^:private idx-regex-to-id (merge aliases
                                      (apply merge (map #(hash-map (s/replace (u/escape-re (s/lower-case (:name %))) #"\s+" "\\\\s+") #{(:license-id %)}) license-list))))

; Store regexes in reverse size order, on the assumption that longer regexes are more specific and should be processed first
; Note: `regexes` actually contains string representations, since regexes in Clojure don't implement equality / hash 🙄
(def ^:private regexes         (reverse (sort-by #(count %) (concat (keys idx-regex-to-id) (keys idx-regex-to-id)))))
(def ^:private re-pattern-mem  (memoize re-pattern))   ; So we memomize re-pattern to save having to recompile the regex string representations every time we use them

(def ids
  "All SPDX license identifiers in the list."
  (keys idx-id-to-info))

(defn id->info
  "Returns the SPDX license information for the given SPDX license identifier, or nil if unable to do so."
  [spdx-id]
  (when spdx-id
    (get idx-id-to-info spdx-id)))

(defn id->spdx-name
  "Returns the official license name for the given SPDX id, or nil if unable to do so."
  [spdx-id]
  (when spdx-id
    (:name (id->info spdx-id))))

(defn spdx-name->id
  "Returns the SPDX license identifier equivalent of the given license name (matched case insensitively), or nil if unable to do so."
  [name]
  (when name
    (get idx-lname-to-id (s/trim (s/lower-case name)))))

(defn uri->id
  "Returns the SPDX license identifier equivalent for the given uri, or nil if unable to do so.

  Notes:
  1. this does not perform exact matching; rather it checks whether the given uri matches the start of any of the known license uris.
  2. uris in the SPDX license list are not unique to a license (approximately 70 out of 600 are duplicates)"
  [uri]
  (when uri
    (let [simplified-uri (u/simplify-uri uri)
          uri-match      (first (filter (partial s/starts-with? simplified-uri) (keys idx-uri-to-id)))]
      (get idx-uri-to-id uri-match))))

(defn spdx-id?
  "Is the given identifier an SPDX identifier?"
  [id]
  (when id
    (not (s/starts-with? id "NON-SPDX"))))

(defn id->name
  "Returns the license name of the given id; either the official SPDX name or (if the id is not an SPDX id) an unofficial name. Returns the id as-is if unable to determine its name."
  [id]
  (if (spdx-id? id)
    (id->spdx-name id)
    (case id
      "NON-SPDX-Public-Domain" "Public domain"
      "NON-SPDX-JDOM"          "JDOM"
      id)))

(defn name->ids
  "Attempts to determine the SPDX license identifier(s) (a set) from the given license name (a string). Returns nil if unable to do so."
  [name]
  (when name
    (let [name (s/trim name)]
      (if-let [exact-id-match (id->info name)]   ; First we exact match on the id, for those cases where someone has used the SPDX id as the name (e.g. in a pom.xml file)
        #{(:license-id exact-id-match)}
        (if-let [exact-name-match (spdx-name->id name)]   ; Then we exact match on the name (albeit case-insensitively)
          #{exact-name-match}
          (get idx-regex-to-id (first (filter #(re-find (re-pattern-mem %) (s/lower-case name)) regexes))))))))   ; Then the last resort is to match on the regexes

(defmulti text->ids
  "Attempts to determine the SPDX license identifier(s) (a set) from the given license text (an InputStream, or something that can have an io/input-stream opened on it)."
  {:arglists '([text])}
  type)

; TODO: https://github.com/pmonks/lice-comb/issues/3
(defmethod text->ids java.io.InputStream
  [is]
  (let [rdr         (io/reader is)    ; Note: we don't wrap this in "with-open", since the input-stream we're handed is closed by the calling fn
        first-lines (s/trim (s/join " " (take 2 (remove s/blank? (map s/trim (line-seq rdr))))))]  ; Take the first two non-blank lines, since many licenses put the name on line 1, and the version on line 2
    (name->ids first-lines)))

(defmethod text->ids :default
  [src]
  (when src
    (with-open [is (io/input-stream src)]
      (text->ids is))))
