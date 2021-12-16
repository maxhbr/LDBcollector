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

(ns lice-comb.files
  "Files related functionality."
  (:require [clojure.string  :as s]
            [clojure.set     :as set]
            [clojure.java.io :as io]
            [lice-comb.spdx  :as spdx]
            [lice-comb.maven :as mvn]
            [lice-comb.utils :as u]))

(defmulti ^:private filename
  "Returns just the name component of the given file or path string, excluding any parents."
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

(def ^:private probable-license-filenames #{"pom.xml" "license" "license.txt" "copying" "unlicense"})   ;TODO: consider "license.md" and #".+\.spdx" (see https://github.com/spdx/spdx-maven-plugin for why the latter is important)...

(defn probable-license-file?
  "Returns true if the given file-like thing (String, File, ZipEntry) is a probable license file, false otherwise."
  [f]
  (let [fname (filename f)]
    (and (not (s/blank? fname))
         (contains? probable-license-filenames (s/lower-case fname)))))

(defn probable-license-files
  "Returns all probable license files in the given directory (as a sequence of java.io.File objects). dir may be a String or a java.io.File, both of which must refer to a directory."
  [dir]
  (when dir
    (let [dir (io/file dir)]
      (if (.exists dir)
        (if (.isDirectory dir)
          (seq (filter #(and (.isFile ^java.io.File %) (probable-license-file? %)) (file-seq (io/file dir))))
          (throw (java.nio.file.NotDirectoryException. (str dir))))
        (throw (java.io.FileNotFoundException. (str dir)))))))

(defmulti file->ids
  "Attempts to determine the SPDX license identifier(s) (a set) from the given file (a String, InputStream, or something that can have an io/input-stream opened on it)."
  {:arglists '([f])}
  filename)

(defmethod file->ids "pom.xml"
  [f]
  (mvn/pom->ids f))

(defmethod file->ids :default
  [f]
  (spdx/text->ids f))

(defn dir->ids
  "Attempt to detect the license(s) in a directory. dir may be a String or a java.io.File, both of which must refer to a directory."
  [dir]
  (u/nset (mapcat file->ids (probable-license-files dir))))

(defn zip->ids
  "Attempt to detect the license(s) in a ZIP file. zip may be a String or a java.io.File, both of which must refer to a ZIP-format compressed file."
  [zip]
  (when zip
    (let [zip (io/file zip)]
      (if (and (.exists zip)
               (.isFile zip))
        (with-open [zip-is (java.util.zip.ZipInputStream. (io/input-stream zip))]
          (loop [entry    (.getNextEntry zip-is)
                 licenses nil]
            (if entry
              (if (probable-license-file? entry)
                (recur (.getNextEntry zip-is) (set/union licenses (file->ids zip-is)))
                (recur (.getNextEntry zip-is) licenses))
              licenses)))
        (throw (java.io.FileNotFoundException. (str zip)))))))
