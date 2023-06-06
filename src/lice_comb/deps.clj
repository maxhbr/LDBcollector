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
            [clojure.reflect :as cr]
            [clojure.edn     :as edn]
            [lice-comb.spdx  :as spdx]
            [lice-comb.maven :as mvn]
            [lice-comb.files :as f]
            [lice-comb.data  :as d]
            [lice-comb.utils :as u]))

(def ^:private overrides-uri (d/uri-for-data "/deps/overrides.edn"))
(def ^:private overrides     (try
                               (edn/read-string (slurp overrides-uri))
                               (catch Exception e
                                 (throw (ex-info (str "Unexpected " (cr/typename (type e)) " while reading " overrides-uri ". Please check your internet connection and try again.") {} e)))))

(def ^:private fallbacks-uri (d/uri-for-data "/deps/fallbacks.edn"))
(def ^:private fallbacks     (try
                               (edn/read-string (slurp fallbacks-uri))
                               (catch Exception e
                                 (throw (ex-info (str "Unexpected " (cr/typename (type e)) " while reading " fallbacks-uri ". Please check your internet connection and try again.") {} e)))))

(defn- check-overrides
  "Checks if an override should be used for the given dep"
  ([ga] (check-overrides ga nil))
  ([ga v]
    (let [gav (symbol (str ga (when v (str "@" v))))]
      (:licenses (get overrides gav (get overrides ga))))))  ; Lookup overrides both with and without the version

(defn- check-fallbacks
  "Checks if a fallback should be used for the given dep, given the set of detected ids"
  [ga ids]
  (if (or (empty? ids)
          (every? #(not (spdx/spdx-id? %)) ids))
    (:licenses (get fallbacks ga {:licenses ids}))
    ids))

(defn- normalise-dep
  "Normalises a dep, by removing any classifier suffixes from the artifact-id (e.g. the $blah suffix in com.foo/bar$blah)."
  [[ga info]]
  (when ga
    [(symbol (first (s/split (str ga) #"\$"))) info]))

(defmulti dep->ids
  "Attempt to detect the license(s) in a tools.deps style dep (a MapEntry or two-element sequence of [groupId/artifactId dep-info])."
  {:arglists '([[ga info]])}
  (fn [[_ info]] (:deps/manifest info)))

(defmethod dep->ids :mvn
  [dep]
  (when dep
    (let [[ga info]              (normalise-dep dep)
          [group-id artifact-id] (s/split (str ga) #"/")
          version                (:mvn/version info)]
      (if-let [override (check-overrides ga version)]
        override
        (let [pom-uri     (mvn/pom-uri-for-gav group-id artifact-id version)
              license-ids (check-fallbacks ga
                                           (if-let [license-ids (mvn/pom->ids pom-uri)]
                                             license-ids
                                             (u/nset (mapcat f/zip->ids (:paths info)))))]      ; If we didn't find any licenses in the dep's POM, check the dep's JAR(s) too
          license-ids)))))

(defmethod dep->ids :deps
  [dep]
  (when dep
    (let [[ga info] (normalise-dep dep)
          version   (:git/sha info)]
      (if-let [override (check-overrides ga version)]
        override
        (check-fallbacks ga (f/dir->ids (:deps/root info)))))))

(defmethod dep->ids nil
  [_])

(defmethod dep->ids :default
  [dep]
  (throw (ex-info (str "Unexpected manifest type '" (:deps/manifest (second dep)) "' for dependency " dep) {:dep dep})))

(defn deps-licenses
  "Attempt to detect the license(s) in a tools.deps 'lib map', returning a new lib map with the licenses assoc'ed in (in key :lice-comb/licenses)"
  [deps]
  (when deps
    (into {}
          (pmap #(let [[k v] %] [k (assoc v :lice-comb/licenses (dep->ids [k v]))]) deps))))
