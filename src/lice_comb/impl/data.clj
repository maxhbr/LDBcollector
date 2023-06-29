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

(ns lice-comb.impl.data
  "Data handling functionality. Note: this namespace is not part of the public
  API of lice-comb and may change without notice."
  (:require [clojure.string  :as s]
            [clojure.java.io :as io]
            [clojure.reflect :as cr]
            [clojure.edn     :as edn]))

(defn load-string-resource
  "Loads the given classpath resources from the classpath, returning it as a
  String. Throws ex-info on error.

  Notes:
  * Classpath resource paths must not start with a forward slash ('/').
  * The JVM does not support hyphens ('-') in classpath resource path elements.
    Use underscore ('_') instead.
  * Unlike during class loading, Clojure does not automatically switch hyphens
    in classpath resource path elements to underscores. This inconsistency can
    be a time-wasting trap."
  [path]
  (when-not (s/blank? path)
    (try
      (if-let [resource (io/resource path)]
        (slurp resource)
        (throw (ex-info (str "No resource found in classpath at " path) {})))
      (catch clojure.lang.ExceptionInfo ie
        (throw ie))
      (catch Exception e
        (throw (ex-info (str "Unexpected " (cr/typename (type e)) " while reading " path) {} e))))))

(defn load-edn-resource
  "Loads and parses the given EDN file from the classpath."
  [path]
  (when-let [edn-string (load-string-resource path)]
    (edn/read-string edn-string)))
