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

(ns lice-comb.deps
  "deps (in tools.deps lib-map format) related functionality."
  (:require [clojure.string  :as s]
            [lice-comb.maven :as mvn]
            [lice-comb.files :as f]
            [lice-comb.utils :as u]))

(defmulti dep->ids
  "Attempt to detect the license(s) in a tools.deps style dep (a MapEntry or two-element sequence of [groupId/artifactId dep-info])."
  {:arglists '([[dep info]])}
  (fn [[_ info]] (:deps/manifest info)))

(defmethod dep->ids :mvn
  [dep]
  (when dep
    (let [[ga info]              dep
          [group-id artifact-id] (s/split (str ga) #"/")
          version                (:mvn/version info)
          pom-uri                (mvn/pom-uri-for-gav group-id artifact-id version)
          license-ids            (mvn/pom->ids pom-uri)]
      (if license-ids
        license-ids
        (u/nset (mapcat f/zip->ids (:paths info)))))))   ; If we didn't find any licenses in the dep's POM, check the dep's JAR(s) too

(defmethod dep->ids :deps
  [[_ info]]
  (when info
    (f/dir->ids (:deps/root info))))

(defmethod dep->ids nil
  [_])

(defmethod dep->ids :default
  [dep]
  (throw (ex-info (str "Unexpected manifest type '" (:deps/manifest (second dep)) "' for dependency " dep) {:dep dep})))

(defn deps-licenses
  "Attempt to detect the license(s) in a tools.deps 'lib map', returning a new lib map with the licenses assoc'ed in (in key :lice-cap/licenses)"
  [deps]
  (when deps
    (into {}
          (for [[k v] deps]
            [k (assoc v :lice-cap/licenses (dep->ids [k v]))]))))
