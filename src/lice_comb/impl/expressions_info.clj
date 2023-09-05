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

(ns lice-comb.impl.expressions-info
  "lice-comb expressions-info map helper functionality. Note: this namespace is
  not part of the public API of lice-comb and may change without notice."
  (:require [clojure.string :as s]))

(defn prepend-source
  "Prepends the given source s (a String) onto all metadata sub-maps in m (a
  lice-comb expressions-info map)."
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
  "Merges any number of lice-comb expressions-info maps, by concatenating and
  de-duping values for the same key (expression)."
  [& maps]
  (let [maps (filter identity maps)]
    (when-not (empty? maps)
      (let [grouped-maps (group-by first (mapcat identity maps))]
        (into {} (map #(vec [% (seq (distinct (mapcat second (get grouped-maps %))))])
                      (keys grouped-maps)))))))
