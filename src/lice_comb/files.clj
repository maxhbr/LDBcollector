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
  "Functionality related to combing files, directories, and ZIP format archives
  for license information."
  (:require [clojure.string                  :as s]
            [clojure.java.io                 :as io]
            [lice-comb.matching              :as lcmtch]
            [lice-comb.maven                 :as lcmvn]
            [lice-comb.impl.expressions-info :as lciei]
            [lice-comb.impl.utils            :as lciu]))

(def ^:private probable-license-filenames #{"pom.xml" "license" "license.txt" "copying" "unlicense"})   ;TODO: consider "license.md" and #".+\.spdx" (see https://github.com/spdx/spdx-maven-plugin for why the latter is important)...

; This is public because it's used in the tests
(defn probable-license-file?
  "Returns true if the given file-like thing (String, File, ZipEntry) is a
  probable license file, false otherwise."
  [f]
  (and (not (nil? f))
       (let [fname (s/lower-case (lciu/filename f))]
         (and (not (s/blank? fname))
              (or (contains? probable-license-filenames fname)
                  (s/ends-with? fname ".pom"))))))

; This is public because it's used in the tests
(defn probable-license-files
  "Returns all probable license files in the given directory, recursively, as a
  set of java.io.File objects. dir may be a String or a java.io.File, either of
  which must refer to a readable directory."
  [dir]
  (when (lciu/readable-dir? dir)
    (some-> (seq (filter #(and (.isFile ^java.io.File %) (probable-license-file? %)) (file-seq (io/file dir))))
            set)))

(defn file->expressions-info
  "Returns an expressions-info map for the given file (an InputStream or
  something that can have an io/input-stream opened on it), or nil if no
  expressions were found.

  If an InputStream is provided, it is the caller's responsibility to open and
  close it, and a filepath associated with the InputStream *must* be provided as
  the second parameter (it is optional for other types of input)."
  ([f] (file->expressions-info f (lciu/filepath f)))
  ([f filepath]
   (when (lciu/readable-file? f)
     (let [fname  (lciu/filename filepath)
           lfname (s/lower-case fname)]
            (lciei/prepend-source filepath
                                  (cond (= lfname "pom.xml")              (lcmvn/pom->expressions-info f fname)
                                        (s/ends-with? lfname ".pom")      (lcmvn/pom->expressions-info f fname)
                                        (instance? java.io.InputStream f) (doall (lcmtch/text->expressions-info f))
                                        :else                             (with-open [is (io/input-stream f)] (doall (lcmtch/text->expressions-info is)))))))))  ; Default is to assume it's a plain text file containing license text(s)

(defn file->expressions
  "Returns a set of SPDX expressions (Strings) for the given file (an
  InputStream or something that can have an io/input-stream opened on it), or
  nil if no expressions were found.

  If an InputStream is provided, it is the caller's responsibility to open and
  close it, and a filepath associated with the InputStream *must* be provided as
  the second parameter (it is optional for other types of input)."
  ([f] (file->expressions f (lciu/filepath f)))
  ([f filepath]
   (some-> (file->expressions-info f filepath)
           keys
           set)))

(defn zip->expressions-info
  "Returns an expressions-info map for the given ZIP file (a String or a File,
  which must refer to a ZIP-format compressed file), or nil if no expressions
  were found.

  Throws if the file is not a valid ZIP."
  [zip]
  (when (lciu/readable-file? zip)
    (let [zip-file (io/file zip)]
      (java.util.zip.ZipFile. zip-file)  ; This no-op forces validation of the zip file - ZipInputStream does not reliably perform validation
      (with-open [zip-is (java.util.zip.ZipInputStream. (io/input-stream zip-file))]
        (loop [result {}
               entry  (.getNextEntry zip-is)]
          (if entry
            (if (probable-license-file? entry)
              (recur (merge result (file->expressions-info zip-is (lciu/filename entry)))
                     (.getNextEntry zip-is))
              (recur result (.getNextEntry zip-is)))
            (when-not (empty? result) (lciei/prepend-source (lciu/filepath zip-file) result))))))))

(defn zip->expressions
  "Returns a set of SPDX expressions (Strings) for the given ZIP file (a String
  or a File, which must refer to a ZIP-format compressed file), or nil if no
  expressions were found.

  Throws if the file is not a valid ZIP."
  [zip]
  (some-> (zip->expressions-info zip)
          keys
          set))

(defn- zip-compressed-files
  "Returns a set of all probable ZIP compressed files (Files) in the given
  directory, recursively, or nil if there are none. dir may be a String or a
  java.io.File, and must refer to a readable directory."
  [dir]
  (when (lciu/readable-dir? dir)
    (some-> (seq (filter #(and (.isFile ^java.io.File %)
                               (or (s/ends-with? (str %) ".zip")
                                   (s/ends-with? (str %) ".jar")))
                         (file-seq (io/file dir))))
            set)))

(defn dir->expressions-info
  "Returns an expressions-info map for the given dir (a String or a File,
  which must refer to a readable directory), or nil if no expressions were
  found.

  The optional `opts` map has these keys:
  * `include-zips?` (boolean, default false) - controls whether zip compressed
    files found in the directory are recursively included in the scan or not"
  ([dir] (dir->expressions-info dir nil))
  ([dir {:keys [include-zips?] :or {include-zips? false}}]
   (when (lciu/readable-dir? dir)
     (lciei/prepend-source (lciu/filepath dir)
                           (let [file-expressions (into {} (map file->expressions-info (probable-license-files dir)))]
                             (if include-zips?
                               (let [zip-expressions (into {} (map #(try (zip->expressions-info %) (catch Exception _ nil)) (zip-compressed-files dir)))]
                                 (merge file-expressions zip-expressions))
                               file-expressions))))))

(defn dir->expressions
  "Returns a set of SPDX expressions (Strings)  for the given dir (a String or
  a File, which must refer to a readable directory), or nil if no expressions
  were found.

  The optional `opts` map has these keys:
  * `include-zips?` (boolean, default false) - controls whether zip compressed
    files found in the directory are recursively included in the scan or not"
  ([dir] (dir->expressions dir nil))
  ([dir opts]
   (some-> (dir->expressions-info dir opts)
           keys
           set)))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning nil. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it."
  []
  (lcmtch/init!)
  (lcmvn/init!)
  nil)
