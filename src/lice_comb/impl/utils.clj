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

(defn mapfonk
  "Returns a new map where f has been applied to all of the keys of m."
  [f m]
  (when m
    (into {}
          (for [[k v] m]
            [(f k) v]))))

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

(defn is-digits?
  "Does the given string contains digits only?"
  [^String s]
  (boolean  ; Eliminate nil-punning
    (when-not (s/blank? s)
      (every? #(Character/isDigit ^Character %) s))))

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

(defn re-concat
  "Concatenate all of the given regexes or strings into a single regex."
  [& res]
  (re-pattern (apply str res)))

(defn base62-encode
  "Encodes the given string to Base62/UTF-8."
  [^String s]
  (when s
    (base62/encode (.getBytes s java.nio.charset.StandardCharsets/UTF_8))))

(defn base62-decode
  "Decodes the given Base62/UTF-8 string."
  [^String s]
  (when s
    (if (re-matches #"\p{Alnum}*" s)
      (java.lang.String. ^bytes (base62/decode s) java.nio.charset.StandardCharsets/UTF_8)
      (throw (ex-info (str "Invalid BASE62 value provided: " s) {})))))   ; Because clj-base62 has crappy error messages

(defn valid-http-uri?
  "Returns true if given string is a valid HTTP or HTTPS URI."
  [s]
  ; Note: no nil check needed since the isValid method handles null sanely
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
              (s/replace #"\Ahttps?://(www\.)?"     "http://")    ; Normalise to http and strip any www. extension on hostname
              (s/replace #"licen[cs]es?"            "license")    ; Alternative spelling and plurals of "license"
              (s/replace #"\.\p{Alpha}\p{Alnum}*\z" "")           ; Strip file type extension (if any)
              (s/replace #"/+\z"                    ""))          ; Strip all trailing forward slash (/) characters
          luri)))))

(defn readable-dir?
  "Is d (a String or File) a readable directory?"
  [d]
  (let [d (io/file d)]
    (and d
         (.exists d)
         (.canRead d)
         (.isDirectory d))))

(defmulti readable-file?
  "Is f (a String, File, InputStream, or Reader) a readable file?"
  type)

(defmethod readable-file? nil
  [_])

(defmethod readable-file? java.io.File
  [^java.io.File f]
  (and f
       (.exists f)
       (.canRead f)
       (not (.isDirectory f))))

(defmethod readable-file? java.lang.String
  [s]
  (or (valid-http-uri? s)
      (readable-file? (io/file s))))

(defmethod readable-file? java.io.InputStream
  [_]
  true)

(defmethod readable-file? java.io.Reader
  [_]
  true)

(defmethod readable-file? java.net.URL
  [_]
  true)

(defmethod readable-file? java.net.URI
  [_]
  true)

(defmulti filepath
  "Returns the full path and name of the given file-like thing (String, File,
  ZipEntry, URI, URL)."
  type)

(defmethod filepath nil
  [_])

(defmethod filepath java.io.File
  [^java.io.File f]
  (.getPath f))

(defmethod filepath java.lang.String
  [s]
  (when s
    (let [s (s/trim s)]
      (if (valid-http-uri? s)
        (filepath (io/as-url s))
        (filepath (io/file   s))))))

(defmethod filepath java.util.zip.ZipEntry
  [^java.util.zip.ZipEntry ze]
  (.getName ze))

(defmethod filepath java.net.URI
  [^java.net.URI uri]
  (str uri))

(defmethod filepath java.net.URL
  [^java.net.URL url]
  (str url))

(defmethod filepath java.io.InputStream
  [_]
  (throw (ex-info "Cannot determine filepath of an InputStream - did you forget to provide it separately?" {})))

(defmulti filename
  "Returns just the name component of the given file-like thing (String, File,
  ZipEntry, URI, URL), excluding any parents."
  type)

(defmethod filename nil
  [_])

(defmethod filename java.io.File
  [^java.io.File f]
  (.getName f))

(defmethod filename java.lang.String
  [s]
  (when s
    (let [s (s/trim s)]
      (if (valid-http-uri? s)
        (filename (io/as-url s))
        (filename (io/file s))))))

(defmethod filename java.util.zip.ZipEntry
  [^java.util.zip.ZipEntry ze]
  (filename (.getName ze)))

(defmethod filename java.net.URI
  [^java.net.URI uri]
  (filename (.getPath uri)))

(defmethod filename java.net.URL
  [^java.net.URL url]
  (filename (.getPath url)))

(defmethod filename java.io.InputStream
  [_]
  (throw (ex-info "Cannot determine filename of an InputStream - did you forget to provide it separately?" {})))

(defn filter-file-seq*
  "As for clojure.core/file-seq, but with support for filtering.  pred must be
  a predicate that accepts one argument of type java.io.File.  Files that don't
  meet pred will not be included in the result, and directories that don't meet
  pred will not be recursed into (so pred must be able to handle both distinct
  cases).

  Note also that dir is always returned, even if it does not meet pred."
  [^java.io.File dir pred]
  (let [pred   (or pred (constantly true))
        filter ^java.io.FileFilter (reify java.io.FileFilter (accept [_ f] (boolean (pred (.getCanonicalFile ^java.io.File f)))))]  ; Use the canonical file, otherwise we will get tripped up by "." being "hidden" according to the JVM when running on a Unix 🤡
    (tree-seq
      (fn [^java.io.File f] (.isDirectory f))
      (fn [^java.io.File d] (seq (.listFiles d filter)))
      dir)))

(defn filter-file-seq
  "As for clojure.core/file-seq, but with support for filtering.  dir-pred
  controls which directories will be included in the result and recursed into.
  file-pred controls which files will be included in the result.  Both must be
  a predicate of one argument of type java.io.File.

  Note also that dir is always returned, even if it does not meet dir-pred."
  [dir dir-pred file-pred]
  (let [dir-pred  (or dir-pred  (constantly true))
        file-pred (or file-pred (constantly true))
        pred      (fn [^java.io.File f]
                    (or (and (.isDirectory f) (dir-pred f))
                        (file-pred f)))]
    (filter-file-seq* dir pred)))

(defn filter-file-only-seq
  "As for clojure.core/file-seq, with support for filtering and only returns
  files (but not any directories that were traversed during the seq).  dir-pred
  controls which directories will be recursed into.  file-pred controls which
  files will be included in the result.  Both must be a predicate of one
  argument of type java.io.File."
  [dir dir-pred file-pred]
  (seq (filter #(.isFile ^java.io.File %) (filter-file-seq dir dir-pred file-pred))))

(defn getenv
  "Obtain the given environment variable, returning default (or nil, if default
  is not provided) if it isn't set."
  ([var] (getenv var nil))
  ([var default]
    (let [val (System/getenv var)]
      (if-not (s/blank? val)
        val
        default))))
