;
; Copyright © 2023 Peter Monks
;
; This Source Code Form is subject to the terms of the Mozilla Public
; License, v. 2.0. If a copy of the MPL was not distributed with this
; file, You can obtain one at https://mozilla.org/MPL/2.0/.
;
; SPDX-License-Identifier: MPL-2.0
;

(ns lice-comb.utils
  "Miscellaneous functionality."
  (:require [clojure.string :as s]))

(def strategy->string
  "A map that turns a matching strategy keyword (as found in an expression-info
  map) into a human readable equivalent.  This is mostly intended for debugging
  / developer informational purposes, and the behaviour may change without
  warning."
  {:spdx-expression                               "SPDX expression"
   :spdx-listed-identifier-exact-match            "SPDX identifier"
   :spdx-listed-identifier-case-insensitive-match "SPDX identifier (case insensitive match)"
   :spdx-matching-guidelines                      "SPDX matching guidelines"
   :spdx-listed-name                              "SPDX listed name (case insensitive match)"
   :spdx-listed-uri                               "SPDX listed URI (relaxed matching)"
   :maven-pom-multi-license-rule                  "Maven POM multiple license conjunction rule"
   :manual-verification                           "manual verification"
   :expression-inference                          "inferred license expression"
   :regex-matching                                "regular expression matching"
   :unidentified                                  "fallback to unidentified LicenseRef"})

(defn expression-info-sort-by-keyfn
  "A [[clojure.core/sort-by]] keyfn for expression-info maps.  This is mostly
  intended for debugging / developer informational purposes, and the behaviour
  may change without warning."
  [m]
  (when m
    (str (case (:id m)
           nil "0"
           "1")
         "-"
         (case (:type m)
           :declared  "0"
           :concluded "1")
         "-"
         (case (:confidence m)
           nil        "0"
           :high      "1"
           :medium    "2"
           :low       "3")
         "-"
         (case (:strategy m)
           :maven-pom-multi-license-rule                  "00"
           :spdx-expression                               "01"
           :spdx-listed-identifier-exact-match            "02"
           :spdx-listed-identifier-case-insensitive-match "03"
           :spdx-matching-guidelines                      "04"
           :spdx-listed-name                              "05"
           :spdx-listed-uri                               "06"
           :manual-verification                           "07"
           :expression-inference                          "08"
           :regex-matching                                "09"
           :unidentified                                  "10"))))

(defn expression-info->string
  "Converts `m`, an expression-info map, into a human-readable `String`.  This
  is mostly intended for debugging / developer informational purposes, and the
  behaviour may change without warning."
  [m expr]
  (when (and m expr)
    (str expr "\n"
      (when-let [info-list (sort-by expression-info-sort-by-keyfn (seq (get m expr)))]
        (s/join "\n" (map #(str (when-let [md-id (:id %)] (when (not= expr md-id) (str "  " md-id " ")))
                                (case (:type %)
                                  :declared  "Declared"
                                  :concluded "Concluded")
                                (when-let [confidence              (:confidence %)]                    (str "\n    Confidence: "       (name confidence)))
                                (when-let [confidence-explanations (seq (:confidence-explanations %))] (str "\n      Explanation(s): " (s/join ", " (map (fn [exp] (s/replace (name exp) "-" " ")) (sort confidence-explanations)))))
                                (when-let [strategy                (:strategy %)]                      (str "\n    Strategy: "         (get strategy->string strategy (name strategy))))
                                (when-let [source                  (seq (:source %))]                  (str "\n    Source:\n    > "    (s/join "\n    > " source))))
                          info-list))))))

(defn expressions-info->string
  "Converts `m`, an expressions-info map, into a human-readable `String`.  This
  is mostly intended for debugging / developer informational purposes, and the
  behaviour may change without warning."
  [m]
  (when m
    (let [exprs (sort (keys m))]
      (s/join "\n\n" (map (partial expression-info->string m) exprs)))))
