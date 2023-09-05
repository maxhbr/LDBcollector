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

(ns lice-comb.lein
  "Functionality related to finding and determining license information from
  dependencies in Leiningen's dependency vector format."
  (:require [dom-top.core                    :as dom]
            [lice-comb.deps                  :as lcd]
            [lice-comb.impl.expressions-info :as lciei]))

(defn- lein-dep->toolsdeps-dep
  "Converts a leiningen style dependency vector into a (partial) tools.deps style
  dependency map. This is partial in that just enough of the tools.deps style
  map is constructed for lice-comb.deps to function."
  [[ga version :as dep]]
  (when dep
    (hash-map ga {:mvn/version version :deps/manifest :mvn})))   ;####TODO: Synthesise :paths key (for paths to JAR files)

(defn dep->expressions-info
  "Attempt to detect the SPDX license expression(s) (a map) in a Leiningen
  style dep (a vector of the form `[groupId/artifactId \"version\"]`)."
  [dep]
  (when-let [toolsdep-dep (lein-dep->toolsdeps-dep dep)]
    (lciei/prepend-source (lcd/dep->expressions-info toolsdep-dep) (pr-str dep))))

(defn dep->expressions
  "Attempt to detect the SPDX license expression(s) (a set) in a Leiningen
  style dep (a vector of the form `[groupId/artifactId \"version\"]`)."
  [dep]
  (some-> (dep->expressions-info dep)
          keys
          set))

(defn deps->expressions-info
  "Attempt to detect all of the SPDX license expression(s) in a Leiningen style
  dependency vector. The result is a map, where each entry in the map has a key
  that is the Leiningen dep, and the value is the lice-comb expressions-info map
  for that dep."
  [deps]
  (into {} (dom/real-pmap #(vec [% (dep->expressions-info %)]) deps)))

(defn deps->expressions-info
  "Attempt to detect all of the SPDX license expression(s) in a Leiningen style
  dependency vector. The result is a map, where each entry in the map has a key
  that is the Leiningen dep, and the value is the set of SPDX license
  expression(s) for that dep."
  [deps]
  (into {} (dom/real-pmap #(vec [% (dep->expressions %)]) deps)))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it."
  []
  (lcd/init!)
  nil)
