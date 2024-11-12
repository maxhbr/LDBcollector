;
; Copyright © 2021 Peter Monks
;
; This Source Code Form is subject to the terms of the Mozilla Public
; License, v. 2.0. If a copy of the MPL was not distributed with this
; file, You can obtain one at https://mozilla.org/MPL/2.0/.
;
; SPDX-License-Identifier: MPL-2.0
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
    be a time-wasting foot gun."
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
