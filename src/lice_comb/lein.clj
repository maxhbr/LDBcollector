;
; Copyright © 2023 Peter Monks
;
; This Source Code Form is subject to the terms of the Mozilla Public
; License, v. 2.0. If a copy of the MPL was not distributed with this
; file, You can obtain one at https://mozilla.org/MPL/2.0/.
;
; SPDX-License-Identifier: MPL-2.0
;

(ns lice-comb.lein
  "Functionality related to combing Leiningen dependency sequences for license
  information."
  (:require [lice-comb.deps                  :as lcd]
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
