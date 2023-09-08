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
  "Functionality related to combing tools.deps dependency maps and lib maps for
  license information."
  (:require [clojure.string                  :as s]
            [dom-top.core                    :as dom]
            [lice-comb.maven                 :as lcmvn]
            [lice-comb.files                 :as lcf]
            [lice-comb.impl.http             :as lcihttp]
            [lice-comb.impl.expressions-info :as lciei]))

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
  "Returns an expressions-info map for the given tools.dep dep (a MapEntry or
  two-element vector of `['groupId/artifactId dep-info]`), or nil if no
  expressions were found."
  {:arglists '([[ga info]])}
  (fn [[_ info]] (:deps/manifest info)))

(defmethod dep->expressions-info :mvn
  [dep]
  (when dep
    (let [[ga info]              (normalise-dep dep)
          [group-id artifact-id] (s/split (str ga) #"/")
          version                (:mvn/version info)
          pom-uri                (lcihttp/gav->pom-uri group-id artifact-id version)
          expressions            (if-let [expressions (lcmvn/pom->expressions-info pom-uri)]
                                   expressions
                                   (into {} (dom/real-pmap lcf/zip->expressions-info (:paths info))))]  ; If we didn't find any licenses in the dep's POM, check the dep's JAR(s)
      (lciei/prepend-source (dep->string dep) expressions))))

(defmethod dep->expressions-info :deps
  [dep]
  (when dep
    (let [[_ info] (normalise-dep dep)]
      (lciei/prepend-source (dep->string dep) (lcf/dir->expressions-info (:deps/root info))))))

(defmethod dep->expressions-info nil
  [_])

(defmethod dep->expressions-info :default
  [dep]
  (throw (ex-info (str "Unexpected manifest type '" (:deps/manifest (second dep)) "' for dependency " dep)
                  {:dep dep})))

(defn dep->expressions
  "Returns a set of SPDX expressions (Strings) for the given tools.dep dep (a
  MapEntry or two-element vector of `['groupId/artifactId dep-info-map]`), or
  nil if no expressions were found."
  [dep]
  (some-> (dep->expressions-info dep)
          keys
          set))

(defn deps-expressions
  "Takes a tools.dep lib map and returns a new lib map with an expressions-info
  map assoc'ed into each dep's info map, in key `:lice-comb/license-info`.
  If no license information was found for a given dep, the lib map entry for
  that dep will be returned unchanged (it will not have the
  `:lice-comb/license-info` key in the info map)."
  [deps]
  (when deps
    (into {} (dom/real-pmap #(if-let [expressions-info (dep->expressions-info %)]
                               (let [[k v] %]
                                 [k (assoc v :lice-comb/license-info expressions-info)])
                               %)
                            deps))))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it."
  []
  (lcmvn/init!)
  (lcf/init!)
  nil)
