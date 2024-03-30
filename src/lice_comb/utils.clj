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

(ns lice-comb.utils
  "Miscellaneous functionality."
  (:require [clojure.string :as s]))

(def strategy->string
  "A map that turns a matching strategy keyword (e.g. as found in an
  expression-info map) into a human readable equivalent.  This is mostly
  intended for debugging / developer discovery purposes, and the behaviour may
  change without warning."
  {:spdx-expression                               "SPDX expression"
   :spdx-listed-identifier-exact-match            "SPDX identifier"
   :spdx-listed-identifier-case-insensitive-match "SPDX identifier (case insensitive match)"
   :spdx-matching-guidelines                      "SPDX matching guidelines"
   :spdx-listed-name                              "SPDX listed name (case insensitive match)"
   :spdx-listed-uri                               "SPDX listed URI (relaxed matching)"
   :expression-inference                          "inferred license expression"
   :regex-matching                                "regular expression matching"
   :unidentified                                  "fallback to unidentified LicenseRef"
   :manual-verification                           "manual verification"})

(defn expression-info-sort-by-keyfn
  "A sort-by keyfn for expression-info maps.  This is mostly intended for
  debugging / developer discovery purposes, and the behaviour may change without
  warning."
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
           :spdx-expression                               "0"
           :spdx-listed-identifier-exact-match            "1"
           :spdx-listed-identifier-case-insensitive-match "2"
           :spdx-matching-guidelines                      "3"
           :spdx-listed-name                              "4"
           :spdx-listed-uri                               "5"
           :manual-verification                           "6"
           :expression-inference                          "7"
           :regex-matching                                "8"
           :unidentified                                  "9"))))

(defn expression-info->string
  "Converts the given expression-info map into a human-readable string, using
  the information in license-info map m.  This is mostly intended for
  debugging / developer discovery purposes, and the behaviour may change without
  warning."
  [m expr]
  (when (and m expr)
    (str expr " "
      (when-let [info-list (sort-by expression-info-sort-by-keyfn (seq (get m expr)))]
        (s/join "\n" (map #(str (when-let [md-id (:id %)] (when (not= expr md-id) (str "  " md-id " ")))
                                (case (:type %)
                                  :declared  "Declared"
                                  :concluded "Concluded")
                                (when-let [confidence (:confidence %)]   (str "\n    Confidence: "    (name confidence)))
                                (when-let [strategy   (:strategy %)]     (str "\n    Strategy: "      (get strategy->string strategy (name strategy))))
                                (when-let [source     (seq (:source %))] (str "\n    Source:\n    > " (s/join "\n    > " source))))
                          info-list))))))

(defn expressions-info->string
  "Converts the given expressions-info map into a human-readable string.  This
  is mostly intended for debugging / developer discovery purposes, and the
  behaviour may change without warning."
  [m]
  (when m
    (let [exprs (sort (keys m))]
      (s/join "\n\n" (map (partial expression-info->string m) exprs)))))
