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
  "Functionality related to combing Leiningen dependency sequences for license
  information."
  (:require [embroidery.api                  :as e]
            [lice-comb.deps                  :as lcd]
            [lice-comb.impl.expressions-info :as lciei]
            [lice-comb.impl.utils            :as lciu]))

(defn- lein-dep->toolsdeps-dep
  "Converts a leiningen style dependency vector into a (partial) tools.deps style
  dependency MapEntry. This is partial in that just enough of the tools.deps style
  info map (in the value) is constructed for lice-comb.deps to function."
  [[ga version :as dep]]
  (when dep
    [ga {:mvn/version version :deps/manifest :mvn}]))   ;####TODO: Synthesise :paths key (for paths to JAR files)

(defn dep->expressions-info
  "Returns an expressions-info map for `dep`, a Leiningen style dep (a vector of
  the form `[groupId/artifactId \"version\"]`), or `nil` if or no expressions
  were found."
  [dep]
  (when-let [toolsdep-dep (lein-dep->toolsdeps-dep dep)]
    (lciei/prepend-source (pr-str dep) (lcd/dep->expressions-info toolsdep-dep))))

(defn dep->expressions
  "Returns a set of SPDX expressions (`String`s) for `dep`. See
  [[dep->expressions-info]] for details."
  [dep]
  (some-> (dep->expressions-info dep)
          keys
          set))

(defn deps->expressions-info
  "Returns a map of expressions-info maps for each Leiningen style dep in
  `deps`.  Each key in the map is a value from `deps`, and the associated value
  is the expressions-info map for that dep (which will be `nil` if no
  expressions were found)."
  [deps]
  (when deps
    (into {} (lciu/file-handle-bounded-pmap #(vec [% (dep->expressions-info %)]) deps))))

(defn deps->expressions
  "Returns a map of sets of SPDX expressions (`String`s) for each Leiningen
  style dep in `deps`. See [[deps->expressions-info]] for details."
  [deps]
  (when deps
    (into {} (lciu/file-handle-bounded-pmap #(vec [% (dep->expressions %)]) deps))))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it.

  Note: this method may have a substantial performance cost."  
  []
  (lcd/init!)
  nil)
