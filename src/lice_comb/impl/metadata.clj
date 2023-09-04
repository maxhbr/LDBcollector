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

(ns lice-comb.impl.metadata
  "Metadata helper functionality. Note: this namespace is not part of
  the public API of lice-comb and may change without notice."
  (:require [clojure.string :as s]))

(defn prepend-source
  "Prepends the given source s (a String) onto all metadata sub-maps in m (a
  lice-comb id+metadata-list map)."
  [m s]
  (if (or (empty? m) (s/blank? s))
    m
    (into {} (map #(if (sequential? (val %))
                     (let [id            (key %)
                           metadata-list (val %)]
                       (hash-map id (map (fn [x] (assoc x :source (conj (seq (:source x)) s))) metadata-list)))
                     %)
                  m))))

(defn merge-maps
  "Merges any number of lice-comb maps, by concatenating and de-duping values
  for the same key (expression)."
  [& maps]
  (let [maps (filter identity maps)]
    (when-not (empty? maps)
      (let [grouped-maps (group-by first (mapcat identity maps))]
        (into {} (map #(vec [% (seq (distinct (mapcat second (get grouped-maps %))))])
                      (keys grouped-maps)))))))

(def ^:private strategies {
  :spdx-expression                               "SPDX expression"
  :spdx-listed-identifier-exact-match            "SPDX identifier"
  :spdx-listed-identifier-case-insensitive-match "SPDX identifier (case insensitive match)"
  :spdx-text-matching                            "SPDX license text matching"
  :spdx-listed-name                              "SPDX listed name (case insensitive match)"
  :spdx-listed-uri                               "SPDX listed URI (relaxed matching)"
  :expression-inference                          "Inferred SPDX expression"
  :regex-matching                                "Regular expression matching"
  :unlisted                                      "Unlisted"})

(defn- metadata-keyfn
  "sort-by keyfn for lice-comb metadata maps"
  [metadata]
  (str (case (:id metadata)
         nil "0"
         "1")
       "-"
       (case (:type metadata)
         :declared  "0"
         :concluded "1")
       "-"
       (case (:confidence metadata)
         nil        "0"
         :high      "1"
         :medium    "2"
         :low       "3")
       "-"
       (case (:strategy metadata)
         :spdx-expression                               "0"
         :spdx-listed-identifier-exact-match            "1"
         :spdx-listed-identifier-case-insensitive-match "2"
         :spdx-text-matching                            "3"
         :spdx-listed-name                              "4"
         :spdx-listed-uri                               "5"
         :expression-inference                          "6"
         :regex-matching                                "7"
         :unlisted                                      "8")))

(defn- metadata-element->string
  "Converts the metadata list for the given identifier into a human-readable
  string."
  [m id]
  (str id ":\n"
    (when-let [metadata-list (sort-by metadata-keyfn (seq (get m id)))]
      (s/join "\n" (map #(str "  "
                              (when-let [md-id (:id %)] (when (not= id md-id) (str md-id " ")))
                              (case (:type %)
                                :declared  "Declared"
                                :concluded "Concluded")
                              (when-let [confidence (:confidence %)]   (str "\n    Confidence: "    (name confidence)))
                              (when-let [strategy   (:strategy %)]     (str "\n    Strategy: "      (get strategies strategy (name strategy))))
                              (when-let [source     (seq (:source %))] (str "\n    Source:\n    > " (s/join "\n    > " source))))
                        metadata-list)))))

(defn metadata->string
  "Converts lice-comb map m into a human-readable string."
  [m]
  (when m
    (let [ids (sort (keys m))]
      (s/join "\n\n" (map (partial metadata-element->string m) ids)))))
