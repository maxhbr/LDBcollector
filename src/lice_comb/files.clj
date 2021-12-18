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

(def ^:private probable-license-filenames #{"pom.xml" "license" "license.txt" "copying" "unlicense"})   ;TODO: consider "license.md" and #".+\.spdx" (see https://github.com/spdx/spdx-maven-plugin for why the latter is important)...

(defn probable-license-file?
  "Returns true if the given file-like thing (String, File, ZipEntry) is a probable license file, false otherwise."
  [f]
  (and (not (nil? f))
       (let [fname (s/lower-case (u/filename f))]
         (and (not (s/blank? fname))
              (or (contains? probable-license-filenames fname)
                  (s/ends-with? fname ".pom"))))))

(defn probable-license-files
  "Returns all probable license files in the given directory, recursively, as a set of java.io.File objects. dir may be a String or a java.io.File, both of which must refer to a directory."
  [dir]
  (when dir
    (let [dir (io/file dir)]
      (if (.exists dir)    ; Note: we have to do this, because file-seq does weird things when handed a file that doesn't exist
        (if (.isDirectory dir)
          (u/nset (filter #(and (.isFile ^java.io.File %) (probable-license-file? %)) (file-seq (io/file dir))))
          (throw (java.nio.file.NotDirectoryException. (str dir))))
        (throw (java.io.FileNotFoundException. (str dir)))))))

(defn file->ids
  "Attempts to determine the SPDX license identifier(s) (a set) from the given file (an InputStream or something that can have an io/input-stream opened on it).
   If an InputStream is provided, the associated filename MUST also be provided as the second parameter."
  ([f] (file->ids f (u/filename f)))
  ([f fname]
   (when (and f fname)
     (let [fname (s/lower-case fname)]
       (cond (= fname "pom.xml")         (mvn/pom->ids f)
             (s/ends-with? fname ".pom") (mvn/pom->ids f)
             :else                       (spdx/text->ids f))))))

(defn dir->ids
  "Attempt to detect the license(s) in a directory. dir may be a String or a java.io.File, both of which must refer to a directory."
  [dir]
  (when dir
    (u/nset (mapcat file->ids (probable-license-files dir)))))

(defn zip->ids
  "Attempt to detect the license(s) in a ZIP file. zip may be a String or a java.io.File, both of which must refer to a ZIP-format compressed file."
  [zip]
  (when zip
    (let [zip-file (io/file zip)]
      (java.util.zip.ZipFile. zip-file)  ; This forces validation of the zip file - ZipInputStream does not reliably perform validation
      (with-open [zip-is (java.util.zip.ZipInputStream. (io/input-stream zip-file))]
        (loop [licenses nil
               entry    (.getNextEntry zip-is)]
          (if entry
            (if (probable-license-file? entry)
              (recur (set/union licenses (file->ids zip-is (u/filename entry))) (.getNextEntry zip-is))
              (recur licenses                                                   (.getNextEntry zip-is)))
            licenses))))))
