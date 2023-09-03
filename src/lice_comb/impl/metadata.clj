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
  (:require [clojure.string                :as s]
            [clojure.set                   :as set]
            [lice-comb.impl.utils          :as lcu]))

(defn prepend-source
  "Prepends the given source (a string) onto the list of sources for all of
  the entries of the metadata for object o. Returns o with the new metadata."
  [o s]
  (if (and o (not (s/blank? s)))
    (if-let [m (meta o)]
      (with-meta o (lcu/mapfonv #(if (map? %) (assoc % :source (conj (seq (:source %)) s)) %) m))
      o)
    o))

(defn- merge-conflicting-key
  "Merges the metadata values for a single key that exists in both m1 and m2."
  [m1 m2 k]
;####TODO: IMPROVE THIS SIMPLISTIC "PICK A WINNER" IMPLEMENTATION!!!!!
  (let [m1v (get m1 k)
        m2v (get m2 k)]
    ; If both values are maps, perhaps lice-comb specific metadata merging
    (if (and (map? m1v) (map? m2v))
      (if (= :declared (:type m1v))
        m1v
        (if (= :declared (:type m2v))
          m2v
          (case [(:confidence m1v) (:confidence m2v)]
            ([:high :high] [:high :medium] [:high :low] [:high nil]) m1v
            ([:medium :medium] [:medium :low] [:medium nil])         m1v
            ([:low :low] [:low nil])                                 m1v
            m2v)))
      (throw (ex-info "Attempt to merge non-lice-comb metadata maps" {})))))


(defn merge-metadata
  "Merges lice-comb metadata maps."
  ([] {})
  ([m] m)
  ([m1 m2]
   (if (and m1 m2)
     (let [keys-in-both    (set/intersection (set (keys m1)) (set (keys m2)))
           keys-in-m1-only (apply disj (set (keys m1)) keys-in-both)
           keys-in-m2-only (apply disj (set (keys m2)) keys-in-both)]
       (merge {}
              (into {} (map #(vec [% (merge-conflicting-key m1 m2 %)]) keys-in-both))
              (into {} (map #(vec [% (get m1 %)]) keys-in-m1-only))
              (into {} (map #(vec [% (get m2 %)]) keys-in-m2-only))))
     (if m1
       m1
       m2)))
  ([m1 m2 & maps]
   (loop [result (merge-metadata m1 m2)
          f      (first maps)
          r      (rest maps)]
     (if f
       (recur (merge-metadata result f) (first r) (rest r))
       result))))

(defn union
  "Equivalent to set/union, but preserves lice-comb metadata from the sets using
  merge-metadata."
  ([] #{})
  ([s] s)
  ([s1 s2]
   (with-meta (set/union s1 s2)
              (merge-metadata (meta s1) (meta s2))))
  ([s1 s2 & sets]
    (let [data     (apply set/union      (concat [s1 s2] sets))
          metadata (apply merge-metadata (concat [(meta s1) (meta s2)] (filter identity (map meta sets))))]
      (with-meta data metadata))))

(def ^:private strategies {
  :spdx-expression                               "SPDX expression"
  :spdx-listed-identifier-exact-match            "SPDX identifier"
  :spdx-listed-identifier-case-insensitive-match "SPDX identifier (case insensitive match)"
  :spdx-text-matching                            "SPDX license text matching"
  :spdx-listed-name                              "SPDX listed name (case insensitive match)"
  :spdx-listed-uri                               "SPDX listed URI (relaxed matching)"
  :regex-name-matching                           "Regular expression name matching"
  :unlisted                                      "Unlisted"})

(defn- metadata-element->string
  "Converts a single element in a lice-comb metadata map (identified by id)
  into a human-readable string."
  [m id]
  (when-let [metadata (get m id)]
    (str id ": "
         (name (:type metadata))
         (when-let [confidence (:confidence metadata)]
           (str "\n  Confidence: " (name confidence)))
         (when-let [strategy (:strategy metadata)]
           (str "\n  Strategy: " (get strategies strategy (str "#### MISSING VALUE: " strategy " ####"))))
         (when-let [source (seq (:source metadata))]
           (str "\n  Source: " (s/join " > " source))))))

(defn metadata->string
  "Converts a lice-comb metadata map m into a human-readable string."
  [m]
  (when m
    (let [ids (sort (keys m))]
      (s/join "\n\n" (map (partial metadata-element->string m) ids)))))
