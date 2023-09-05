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

(def ^:private strategy->string {
  :spdx-expression                               "SPDX expression"
  :spdx-listed-identifier-exact-match            "SPDX identifier"
  :spdx-listed-identifier-case-insensitive-match "SPDX identifier (case insensitive match)"
  :spdx-text-matching                            "SPDX license text matching"
  :spdx-listed-name                              "SPDX listed name (case insensitive match)"
  :spdx-listed-uri                               "SPDX listed URI (relaxed matching)"
  :expression-inference                          "inferred SPDX expression"
  :regex-matching                                "regular expression matching"
  :unlisted                                      "fallback to unlisted LicenseRef"})

(defn- info-keyfn
  "sort-by keyfn for lice-comb info maps"
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

(defn- license-info-element->string
  "Converts the info list for the given identifier into a human-readable
  string, using the information in license-info map m."
  [m id]
  (str id ":\n"
    (when-let [info-list (sort-by info-keyfn (seq (get m id)))]
      (s/join "\n" (map #(str "  "
                              (when-let [md-id (:id %)] (when (not= id md-id) (str md-id " ")))
                              (case (:type %)
                                :declared  "Declared"
                                :concluded "Concluded")
                              (when-let [confidence (:confidence %)]   (str "\n    Confidence: "    (name confidence)))
                              (when-let [strategy   (:strategy %)]     (str "\n    Strategy: "      (get strategy->string strategy (name strategy))))
                              (when-let [source     (seq (:source %))] (str "\n    Source:\n    > " (s/join "\n    > " source))))
                        info-list)))))

(defn license-info->string
  "Converts lice-comb license-info map m into a human-readable string.  This
  function is mostly intended for debugging / developer discovery purposes, and
  the content and format of the output may change without warning."
  [m]
  (when m
    (let [ids (sort (keys m))]
      (s/join "\n\n" (map (partial license-info-element->string m) ids)))))
