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
            [clojure.tools.logging           :as log]
            [embroidery.api                  :as e]
            [lice-comb.matching              :as lcm]
            [lice-comb.maven                 :as lcmvn]
            [lice-comb.impl.expressions-info :as lciei]
            [lice-comb.impl.utils            :as lciu]))

(def ^:private probable-license-filenames #{"pom.xml" "license" "license.txt" "copying" "unlicense"})   ;TODO: consider "license.md" and #".+\.spdx" (see https://github.com/spdx/spdx-maven-plugin for why the latter is important)...

; This is public because it's used in the tests
(defn probable-license-file?
  "Returns `true` if the given file-like thing (`String` containing a filename,
  `File`, `ZipEntry`) is a probable license file, false otherwise."
  [f]
  (and (not (nil? f))  ; Use this idiom to ensure a boolean value is returned, not nil
       (let [fname (s/lower-case (lciu/filename f))]
         (and (not (s/blank? fname))
              (or (contains? probable-license-filenames fname)
                  (s/ends-with? fname ".pom"))))))

; This is public because it's used in the tests
(defn probable-license-files
  "Returns all probable license files in the given directory, recursively, as a
  set of `File` objects. `dir` may be a `String` or a `File`, either of
  which must refer to a readable directory.

  The optional `opts` map has these keys:
  * `include-hidden-dirs?` (boolean, default `false`) - controls whether hidden
    directories (as defined by `java.io.File.isHidden()`) are included in the
    search or not."
  ([dir] (probable-license-files dir nil))
  ([dir {:keys [include-hidden-dirs?] :or {include-hidden-dirs? false} :as opts}]
   (when (lciu/readable-dir? dir)
     (some-> (lciu/filter-file-only-seq (io/file dir)
                                        (fn [^java.io.File d] (and (not= (.getCanonicalFile d) (.getCanonicalFile (io/file (lcmvn/local-maven-repo))))  ; Make sure to exclude the Maven local repo, just in case it happens to be nested within dir
                                                                   (or include-hidden-dirs? (not (.isHidden d)))))
                                        probable-license-file?)
             set))))

(defn file->expressions-info
  "Returns an expressions-info map for `f` (an `InputStream` or something that
  can have an `clojure.java.io/input-stream` opened on it), or `nil` if no
  expressions were found.

  If an `InputStream` is provided, it is the caller's responsibility to open and
  close it, and a filepath associated with the `InputStream` *must* be provided
  as the second parameter (it is not required for other types of input)."
  ([f] (file->expressions-info f (lciu/filepath f)))
  ([f filepath]
   (when (lciu/readable-file? f)
     (let [fname  (lciu/filename filepath)
           lfname (s/lower-case fname)]
            (lciei/prepend-source filepath
                                  (cond (or (= lfname "pom.xml")
                                            (s/ends-with? lfname ".pom")) (doall (lcmvn/pom->expressions-info f fname))
                                        (instance? java.io.InputStream f) (doall (lcm/text->expressions-info f))
                                        :else                             (with-open [is (io/input-stream f)] (doall (lcm/text->expressions-info is)))))))))  ; Default is to assume it's a plain text file containing license text(s)

(defn file->expressions
  "Returns a set of SPDX expressions (`String`s) for `f`. See
   [[file->expressions-info]] for details."
  ([f] (file->expressions f (lciu/filepath f)))
  ([f filepath]
   (some-> (file->expressions-info f filepath)
           keys
           set)))

(defn zip->expressions-info
  "Returns an expressions-info map for `zip` (a `String` or `File`, which must
  refer to a ZIP-format compressed file), or `nil` if no expressions were found.

  Throws various Java IO exceptions if the file is not a valid ZIP-format file."
  [zip]
  (when (lciu/readable-file? zip)
    (let [zip-file (io/file zip)]
      (java.util.zip.ZipFile. zip-file)  ; This no-op forces validation of the zip file - ZipInputStream does not reliably perform validation
      (with-open [zip-is (java.util.zip.ZipInputStream. (io/input-stream zip-file))]
        (loop [result {}
               entry  (.getNextEntry zip-is)]
          (if entry
            (if (probable-license-file? entry)
              (if-let [expressions (try
                                     (file->expressions-info zip-is (lciu/filename entry))
                                     (catch Exception e
                                       (log/warn (str "Unexpected exception while processing " (lciu/filename zip) ":" (lciu/filename entry) " - ignoring") e)
                                       nil))]
                (recur (merge result expressions) (.getNextEntry zip-is))
                (recur result (.getNextEntry zip-is)))
              (recur result (.getNextEntry zip-is)))
            (when-not (empty? result) (lciei/prepend-source (lciu/filepath zip-file) result))))))))

(defn zip->expressions
  "Returns a set of SPDX expressions (`String`s) for `zip`. See
  [[zip->expressions-info]] for details."
  [zip]
  (some-> (zip->expressions-info zip)
          keys
          set))

(defn- zip-compressed-files
  "Returns a set of all probable ZIP compressed files (Files) in `dir`,
  recursively, or `nil` if there are none. `dir` may be a `String` or a
  `File`, and must refer to a readable directory.

  The optional `opts` map has these keys:
  * `include-hidden-dirs?` (boolean, default `false`) - controls whether hidden
    directories (as defined by `java.io.File.isHidden()`) are included in the
    search or not."
  ([dir] (zip-compressed-files dir nil))
  ([dir  {:keys [include-hidden-dirs?] :or {include-hidden-dirs? false} :as opts}]
   (when (lciu/readable-dir? dir)
      (some-> (lciu/filter-file-only-seq (io/file dir)
                                         (fn [^java.io.File d] (or include-hidden-dirs? (not (.isHidden d))))
                                         (fn [^java.io.File f]
                                           (let [lname (s/lower-case (.getName f))]
                                             (or (s/ends-with? lname ".zip")
                                                 (s/ends-with? lname ".jar")))))
              set))))

(defn dir->expressions-info
  "Returns an expressions-info map for `dir` (a `String` or `File`, which must
  refer to a readable directory), or `nil` if or no expressions were found.

  The optional `opts` map has these keys:
  * `include-hidden-dirs?` (boolean, default `false`) - controls whether hidden
    directories (as defined by `java.io.File.isHidden()`) are included in the
    search or not.
  * `include-zips?` (boolean, default `false`) - controls whether zip compressed
    files found in the directory are recursively included in the scan or not

  Note: logs and ignores errors (XML parsing errors, ZIP file errors, etc.)"
  ([dir] (dir->expressions-info dir nil))
  ([dir {:keys [include-hidden-dirs? include-zips?] :or {include-hidden-dirs? false include-zips? false} :as opts}]
   (when (lciu/readable-dir? dir)
     (let [file-expressions (into {} (filter identity (e/pmap* #(try
                                                                  (file->expressions-info %)
                                                                  (catch Exception e
                                                                    (log/warn (str "Unexpected exception while processing " % " - ignoring") e)
                                                                    nil))
                                                               (probable-license-files dir opts))))]
       (if include-zips?
         (let [zip-expressions (into {} (filter identity (e/pmap* #(try
                                                                     (zip->expressions-info %)
                                                                     (catch Exception e
                                                                       (log/warn (str "Unexpected exception while processing " % " - ignoring") e)
                                                                       nil))
                                                                  (zip-compressed-files dir opts))))]
           (lciei/prepend-source (lciu/filepath dir) (merge file-expressions zip-expressions)))
         (lciei/prepend-source (lciu/filepath dir) file-expressions))))))

(defn dir->expressions
  "Returns a set of SPDX expressions (`String`s) for `dir`. See
  [[dir->expressions-info]] for details."
  ([dir] (dir->expressions dir nil))
  ([dir opts]
   (some-> (dir->expressions-info dir opts)
           keys
           set)))

(defn init!
  "Initialises this namespace upon first call (and does nothing on subsequent
  calls), returning `nil`. Consumers of this namespace are not required to call
  this fn, as initialisation will occur implicitly anyway; it is provided to
  allow explicit control of the cost of initialisation to callers who need it.

  Note: this method may have a substantial performance cost."
  []
  (lcm/init!)
  (lcmvn/init!)
  nil)
