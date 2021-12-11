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

(ns lice-comb.utils
  "General purpose utility fns that I seem to end up needing in every single project I write..."
  (:require [clojure.string :as s]))

(defn clojurise-json-key
  "Converts JSON-style string keys (e.g. \"fullName\") to Clojure keyword keys (e.g. :full-name)."
  [k]
  (when k
    (keyword
      (s/replace
        (s/join "-"
                (map s/lower-case
                     (s/split k #"(?<!(^|[A-Z]))(?=[A-Z])|(?<!^)(?=[A-Z][a-z])")))
        "_"
        "-"))))

(defn mapfonk
  "Returns a new map where f has been applied to all of the keys of m."
  [f m]
  (when (and f m)
    (into {}
          (for [[k v] m]
            [(f k) v]))))

(defn mapfonv
  "Returns a new map where f has been applied to all of the values of m."
  [f m]
  (when (and f m)
    (into {}
          (for [[k v] m]
            [k (f v)]))))

(defn escape-re
  "Escapes the given string for use in a regex."
  [s]
  (when s
    (s/escape s {\< "\\<"
                 \( "\\("
                 \[ "\\["
                 \{ "\\{"
                 \\ "\\\\"
                 \^ "\\^"
                 \- "\\-"
                 \= "\\="
                 \$ "\\$"
                 \! "\\!"
                 \| "\\|"
                 \] "\\]"
                 \} "\\}"
                 \) "\\)"
                 \? "\\?"
                 \* "\\*"
                 \+ "\\+"
                 \. "\\."
                 \> "\\>"
                 })))

(defn simplify-uri
  "Simplifies a URI (which can be a string, java.net.URL, or java.net.URI). Returns a string."
  [uri]
  (when uri
    (s/replace (s/replace (s/lower-case (s/trim (str uri)))
                          "https://" "http://")
               "://www." "://")))
