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

(ns lice-comb.impl.utils
  "General purpose utility fns that I seem to end up needing in every single
  project I write... Note: this namespace is not part of the public API of
  lice-comb and may change without notice."
  (:require [clojure.string  :as s]
            [clojure.java.io :as io]
            [clj-base62.core :as base62]))

(defn mapfonv
  "Returns a new map where f has been applied to all of the values of m."
  [f m]
  (when m
    (into {}
          (for [[k v] m]
            [k (f v)]))))

(defn map-pad
  "Like map, but when presented with multiple collections of different lengths,
  'pads out' the missing elements with nil rather than terminating early."
  [f & cs]
  (loop [result nil
         firsts (map first cs)
         rests  (map rest  cs)]
    (if-not (seq (keep identity firsts))
      result
      (recur (cons (apply f firsts) result)
             (map first rests)
             (map rest  rests)))))

(defn strim
  "nil safe version of clojure.string/trim"
  [^String s]
  (when s (s/trim s)))

(defn nset
  "nil preserving version of clojure.core/set"
  [coll]
  (some-> (seq coll)
          set))

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

(defn base62-encode
  "Encodes the given string to Base62/UTF-8."
  [^String s]
  (when s
    (base62/encode (.getBytes s (java.nio.charset.StandardCharsets/UTF_8)))))

(defn base62-decode
  "Decodes the given Base62/UTF-8 string."
  [^String s]
  (when s
    (java.lang.String. ^bytes (base62/decode s) (java.nio.charset.StandardCharsets/UTF_8))))

(defn valid-http-uri?
  "Returns true if given string is a valid HTTP or HTTPS URI."
  [^String s]
  ; Note: no nil check needed since the isValid method handles nil sanely
  (.isValid (org.apache.commons.validator.routines.UrlValidator. ^"[Ljava.lang.String;" (into-array String ["http" "https"])) s))

(defn simplify-uri
  "Simplifies a URI (which can be a string, java.net.URL, or java.net.URI) if
  possible, returning a String. Returns nil if the input is nil or blank."
  [uri]
  (let [uri (str uri)]
    (when-not (s/blank? uri)
      (let [luri (s/lower-case (s/trim uri))]
        (if (valid-http-uri? luri)
          (-> luri
              (s/replace #"\Ahttps?://(www\.)?" "http://")  ; Normalise to http and strip any www. extension on hostname
              (s/replace #"\.[\p{Alnum}]{3,}\z" ""))        ; Strip file type extension (if any)
          luri)))))

(defmulti filename
  "Returns just the name component of the given file or path string, excluding
  any parents."
  type)

(defmethod filename nil
  [_])

(defmethod filename java.io.File
  [^java.io.File f]
  (.getName f))

(defmethod filename java.lang.String
  [s]
  (filename (io/file s)))

(defmethod filename java.util.zip.ZipEntry
  [^java.util.zip.ZipEntry ze]
  (filename (.getName ze)))   ; Note that Zip Entry names include the entire path

(defmethod filename java.net.URI
  [^java.net.URI uri]
  (filename (.getPath uri)))

(defmethod filename java.net.URL
  [^java.net.URL url]
  (filename (.getPath url)))

(defmethod filename java.io.InputStream
  [_]
  (throw (ex-info "Cannot determine filename of an InputStream - did you forget to provide it separately?" {})))

(defn getenv
  "Obtain the given environment variable, returning default (or nil, if default
  is not provided) if it isn't set."
  ([var] (getenv var nil))
  ([var default]
    (let [val (System/getenv var)]
      (if-not (s/blank? val)
        val
        default))))
