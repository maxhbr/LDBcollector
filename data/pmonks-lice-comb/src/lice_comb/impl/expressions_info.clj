;
; Copyright © 2023 Peter Monks
;
; This Source Code Form is subject to the terms of the Mozilla Public
; License, v. 2.0. If a copy of the MPL was not distributed with this
; file, You can obtain one at https://mozilla.org/MPL/2.0/.
;
; SPDX-License-Identifier: MPL-2.0
;

(ns lice-comb.impl.expressions-info
  "lice-comb expressions-info map helper functionality. Note: this namespace is
  not part of the public API of lice-comb and may change without notice."
  (:require [clojure.string   :as s]
            [spdx.expressions :as sexp]))

(defn prepend-source
  "Prepends the given source s (a String) onto the :source sequence of all
  expression-info sub-maps in m (an expressions-info map)."
  [s m]
  (if (or (s/blank? s) (empty? m))
    m
    (into {} (map #(if (sequential? (val %))
                     (let [id            (key %)
                           metadata-list (val %)]
                       (hash-map id (map (fn [x] (assoc x :source (let [old-source (seq (:source x))
                                                                        new-source (if (not= s (first old-source))  ; Only add s if it isn't already there
                                                                                     (conj old-source s)
                                                                                     old-source)]
                                                                    new-source)))
                                         metadata-list)))
                     %)
                  m))))

(defn merge-maps
  "Merges any number of expressions-info maps, by concatenating and de-duping
  values for the same key (expression). Returns a single map that may contain
  multiple map entries."
  [& maps]
  (let [maps (filter identity maps)]
    (when-not (empty? maps)
      (let [grouped-maps (group-by first (mapcat identity maps))]
        (into {} (map #(vec [% (seq (distinct (mapcat second (get grouped-maps %))))])
                      (keys grouped-maps)))))))

(defn join-maps-with-operator
  "Joins `eim`, an expressions-info map with multiple entries into an
  expressions-info map with a single entry that is an SPDX expression joining
  all of the entries via SPDX operator `op` (either :and or :or)."
  [op eim]
  (when (and op eim)
    (if (<= (count eim) 1)
      eim
      (let [new-expr (sexp/normalise (s/join (str " " (s/upper-case (name op)) " ") (keys eim)))
            new-ei   (apply concat (vals eim))]
        {new-expr new-ei}))))

(def ^:private confidence-sort {
  :low    0
  :medium 1
  :high   2})

(defn sort-confidences
  "Sorts a sequence of confidences from low to high."
  [cs]
  (when cs
    (sort-by confidence-sort cs)))

(defn lowest-confidence
  "Returns the lowest confidence in a sequence of confidences."
  [cs]
  (when cs
    (first (sort-confidences cs))))

(defn highest-confidence
  "Returns the highest confidence in a sequence of confidences."
  [cs]
  (when cs
    (last (sort-confidences cs))))

(defn calculate-confidence-for-expression
  "Calculate the confidence for an expression, as the lowest confidence in the
  expression-infos for the identifiers that make up the expression."
  [expression-infos]
  (if-let [confidence (lowest-confidence (filter identity (map :confidence expression-infos)))]
    confidence
    :high))   ; For when none of the components have a confidence (i.e. they're all :type :declared)
