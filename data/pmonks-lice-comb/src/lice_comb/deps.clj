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
            [clojure.tools.logging           :as log]
            [lice-comb.maven                 :as lcmvn]
            [lice-comb.files                 :as lcf]
            [lice-comb.impl.expressions-info :as lciei]
            [lice-comb.impl.utils            :as lciu]))

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

(defn- expressions-from-dep
  "Find license expressions in the given dep, ignoring exceptions."
  [dep]
  (when dep
    (let [[ga info]              (normalise-dep dep)
          [group-id artifact-id] (s/split (str ga) #"/")
          version                (:mvn/version info)]
      (if-let [gav-expressions (try
                                 (lcmvn/gav->expressions-info group-id artifact-id version)
                                 (catch javax.xml.stream.XMLStreamException xse
                                   (log/warn (str "Failed to parse POM for " group-id "/" artifact-id (when version (str "@" version)) " - ignoring") xse)
                                   nil))]
        gav-expressions
        ; If we didn't find any licenses in the dep's POM, check the dep's JAR(s)
        (into {} (filter identity
                         (lciu/file-handle-bounded-pmap
                           #(try
                              (lcf/zip->expressions-info %)
                              (catch javax.xml.stream.XMLStreamException xse
                                (log/warn (str "Failed to parse pom inside " % " - ignoring") xse)
                                nil)
                              (catch java.util.zip.ZipException ze
                                (log/warn (str "Failed to unzip " % " - ignoring") ze)
                                nil))
                           (:paths info))))))))

(defmulti dep->expressions-info
  "Returns an expressions-info map for `dep` (a `MapEntry` or two-element vector
  of `['group-id/artifact-id dep-info]`), or `nil` if no expressions were found."
  {:arglists '([[ga info :as dep]])}
  (fn [[_ info]] (:deps/manifest info)))

(defmethod dep->expressions-info :mvn
  [dep]
  (when-let [expressions (expressions-from-dep dep)]
    (lciei/prepend-source (dep->string dep) expressions)))

(defmethod dep->expressions-info :deps
  [dep]
  (let [[_ info] (normalise-dep dep)]
    (lciei/prepend-source (dep->string dep) (lcf/dir->expressions-info (:deps/root info)))))

(defmethod dep->expressions-info nil
  [[ga _ :as dep]]
  (let [[normalised-ga _]      (normalise-dep dep)
        [group-id artifact-id] (s/split (str normalised-ga) #"/")
        version                (lcmvn/ga-latest-version group-id artifact-id)]
    (when version
      (let [gav-expressions    (try
                                 (lcmvn/gav->expressions-info group-id artifact-id version)
                                 (catch javax.xml.stream.XMLStreamException xse
                                   (log/warn (str "Failed to parse POM for " group-id "/" artifact-id (when version (str "@" version)) " - ignoring") xse)
                                   nil))]
        (lciei/prepend-source (str ga "@" version) gav-expressions)))))

(defmethod dep->expressions-info :default
  [[_ info :as dep]]
  (throw (ex-info (str "Unexpected manifest type '" (:deps/manifest info) "' for dependency " dep)
                  {:dep dep})))

(defn dep->expressions
  "Returns a set of SPDX expressions (`String`s) for `dep`. See
  [[dep->expressions-info]] for details."
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
    (into {} (pmap #(if-let [expressions-info (dep->expressions-info %)]
                      (let [[k v] %]
                        [k (assoc v :lice-comb/license-info expressions-info)])
                      %)
                   deps))))

(defn dep->pom-uri
  "Returns a `URI` that points to the pom for `dep` (a `MapEntry` or two-element
  vector of `['group-id/artifact-id dep-info]`), or `nil` if `dep` is not a
  Maven dep, or a POM could not be found for it.  When non-`nil`, the returned
  URI is guaranteed to be resolvable - either to a file that exists in the local
  Maven cache, or to an HTTP-accessible resource on a remote Maven artifact
  repository (e.g. Maven Central or Clojars)."
  [dep]
  (when (and dep
             (= :mvn (:deps/manifest (second dep))))
    (let [[ga info]              (normalise-dep dep)
          [group-id artifact-id] (s/split (str ga) #"/")
          version                (:mvn/version info)]
      (lcmvn/gav->pom-uri group-id artifact-id version))))

(defmulti dep->locations
  "Returns a sequence of `String`s representing locations that may be searched
  for license information for `dep` (a `MapEntry` or two-element vector of
  `['group-id/artifact-id dep-info]`), or `nil` if no locations were found."
  {:arglists '([[ga info :as dep]])}
  (fn [[_ info]] (:deps/manifest info)))

(defmethod dep->locations :mvn
  [[ga info]]
  (let [[group-id artifact-id] (s/split (str ga) #"/")
         version               (:mvn/version info)]
    (seq (filter identity (concat (list (lcmvn/gav->pom-uri group-id artifact-id version)) (:paths info))))))

(defmethod dep->locations :deps
  [[_ info]]
  (seq (filter identity (list (:deps/root info)))))

(defmethod dep->locations nil
  [[ga _]]
  (let [[group-id artifact-id] (s/split (str ga) #"/")]
    (seq (filter identity (list (lcmvn/gav->pom-uri group-id artifact-id))))))

(defmethod dep->locations :default
  [[_ info :as dep]]
  (throw (ex-info (str "Unexpected manifest type '" (:deps/manifest info) "' for dependency " dep)
                  {:dep dep})))

(defmulti dep->version
  "Returns the Maven version (as a `String`) for `dep` (a `MapEntry` or
  two-element vector of `['group-id/artifact-id dep-info]`), or `nil` if no
  version was found."
  {:arglists '([[ga info :as dep]])}
  (fn [[_ info]] (:deps/manifest info)))

(defmethod dep->version :mvn
  [[_ info]]
  (:mvn/version info))

(defmethod dep->version :deps
  [[_ info]]
  (str (:git/sha info) (when-let [tag (:git/tag info)] (str "/" tag))))

(defmethod dep->version nil
  [[ga _]]
  (let [[group-id artifact-id] (s/split (str ga) #"/")]
    (lcmvn/ga-latest-version group-id artifact-id)))

(defmethod dep->version :default
  [[_ info :as dep]]
  (throw (ex-info (str "Unexpected manifest type '" (:deps/manifest info) "' for dependency " dep)
                  {:dep dep})))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning `nil`. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it.

  Note: this method may have a substantial performance cost."
  []
  (lcmvn/init!)
  (lcf/init!)
  nil)
