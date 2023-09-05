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
  "Functionality related to finding and determining license information from
  dependencies in tools.deps lib-map format."
  (:require [clojure.string                  :as s]
            [dom-top.core                    :as dom]
            [spdx.licenses                   :as sl]
            [lice-comb.maven                 :as lcmvn]
            [lice-comb.files                 :as lcf]
            [lice-comb.impl.data             :as lcd]
            [lice-comb.impl.expressions-info :as lciei]))

;####TODO: FIGURE OUT HOW TO HANDLE METADATA FOR OVERRIDES / FALLBACKS!!!!
;(def ^:private overrides-d (delay (lcd/load-edn-resource "lice_comb/deps/overrides.edn")))
;(def ^:private fallbacks-d (delay (lcd/load-edn-resource "lice_comb/deps/fallbacks.edn")))

;(defn- check-overrides
;  "Checks if an override should be used for the given dep"
;  ([ga] (check-overrides ga nil))
;  ([ga v]
;    (let [gav (symbol (str ga (when v (str "@" v))))]
;      (:licenses (get @overrides-d gav (get @overrides-d ga))))))  ; Lookup overrides both with and without the version

;(defn- check-fallbacks
;####TODO: UPDATE FOR license-info MAP RATHER THAN ID SET
;  "Checks if a fallback should be used for the given dep, given the set of
;  detected ids"
;  [ga ids]
;  (if (or (empty? ids)
;          (every? #(not (sl/listed-id? %)) ids))
;    (:licenses (get @fallbacks-d ga {:licenses ids}))
;    ids))

(defn- normalise-dep
  "Normalises a dep, by removing any classifier suffixes from the artifact-id
  (e.g. the $blah suffix in com.foo/bar$blah)."
  [[ga info]]
  (when ga
    [(symbol (first (s/split (str ga) #"\$"))) info]))

(defmulti ^:private dep->string
  "Converts a dep to a string."
  {:arglists '([[ga info]])}
  (fn [[_ info]] (:deps/manifest info)))

(defmethod ^:private dep->string :mvn
  [[ga info]]
  (str ga "@" (:mvn/version info)))

(defmethod ^:private dep->string :deps
  [[ga info]]
  (str ga "@" (:git/sha info) (when-let [tag (:git/tag info)] (str "/" tag))))

(defmulti dep->expressions-info
  "Attempt to detect the SPDX license expression(s) (a map) in a tools.deps
  style dep (a MapEntry or two-element sequence of
  `[groupId/artifactId dep-info]`).

  The result has metadata attached that describes how the identifiers in the
  expression(s) were determined."
  {:arglists '([[ga info]])}
  (fn [[_ info]] (:deps/manifest info)))

(defmethod dep->expressions-info :mvn
  [dep]
  (when dep
    (let [[ga info]              (normalise-dep dep)
          [group-id artifact-id] (s/split (str ga) #"/")
          version                (:mvn/version info)]
;      (if-let [override (check-overrides ga version)]
;        override
        (let [pom-uri     (lcmvn/pom-uri-for-gav group-id artifact-id version)
              expressions ;(check-fallbacks ga
                                           (if-let [expressions (lcmvn/pom->expressions-info pom-uri)]
                                             expressions
                                             (into {} (dom/real-pmap lcf/zip->expressions-info (:paths info))));)  ; If we didn't find any licenses in the dep's POM, check the dep's JAR(s)
                                                ]
          (lciei/prepend-source expressions (dep->string dep))))));)

(defmethod dep->expressions-info :deps
  [dep]
  (when dep
    (let [[ga info] (normalise-dep dep)
          version   (:git/sha info)]
;      (if-let [override (check-overrides ga version)]
;        override
;        (check-fallbacks ga
          (lciei/prepend-source (lcf/dir->expressions-info (:deps/root info)) (dep->string dep)))));))

(defmethod dep->expressions-info nil
  [_])

(defmethod dep->expressions-info :default
  [dep]
  (throw (ex-info (str "Unexpected manifest type '" (:deps/manifest (second dep)) "' for dependency " dep)
                  {:dep dep})))

(defn dep->expressions
  "Attempt to detect the SPDX license expression(s) (a set) in a tools.deps
  style dep (a MapEntry or two-element sequence of
  `[groupId/artifactId dep-info]`).

  The result has metadata attached that describes how the identifiers in the
  expression(s) were determined."
  [dep]
  (some-> (dep->expressions-info dep)
          keys
          set))

(defn deps-expressions
  "Attempt to detect the SPDX license expression(s) in a tools.deps 'lib map',
  returning a new lib map with the licenses assoc'ed in (in key
  `:lice-comb/license-info`)"
  [deps]
  (when deps
    (into {} (dom/real-pmap #(let [[k v] %] [k (assoc v :lice-comb/license-info (dep->expressions-info [k v]))]) deps))))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it."
  []
  (lcmvn/init!)
  (lcf/init!)
;  @overrides-d
;  @fallbacks-d
  nil)
