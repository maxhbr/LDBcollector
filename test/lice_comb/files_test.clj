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

(ns lice-comb.files-test
  (:require [clojure.test               :refer [deftest testing is use-fixtures]]
            [clojure.java.io            :as io]
            [lice-comb.test-boilerplate :refer [fixture]]
            [lice-comb.files            :refer [probable-license-file? probable-license-files file->ids dir->ids zip->ids]]))

(use-fixtures :once fixture)

(def test-data-path "./test/lice_comb/data")

(deftest probable-license-file?-tests
  (testing "Nil, empty or blank names"
    (is (= false (probable-license-file? nil)))
    (is (= false (probable-license-file? "")))
    (is (= false (probable-license-file? "       ")))
    (is (= false (probable-license-file? "\n")))
    (is (= false (probable-license-file? "\t"))))
  (testing "Filenames that are probable license files"
    (is (= true  (probable-license-file? "pom.xml")))
    (is (= true  (probable-license-file? "POM.XML")))
    (is (= true  (probable-license-file? "asf-cat-1.0.12.pom")))
    (is (= true  (probable-license-file? "license")))
    (is (= true  (probable-license-file? "LICENSE")))
    (is (= true  (probable-license-file? "license.txt")))
    (is (= true  (probable-license-file? "LICENSE.TXT")))
    (is (= true  (probable-license-file? "copying")))
    (is (= true  (probable-license-file? "COPYING"))))
  (testing "Filenames that are not probable license files"
    (is (= false (probable-license-file? "NOTICES")))
    (is (= false (probable-license-file? "notices")))
    (is (= false (probable-license-file? "licenses")))
    (is (= false (probable-license-file? "LICENSES")))
    (is (= false (probable-license-file? "deps.edn")))
    (is (= false (probable-license-file? "pm.xml"))))
  (testing "Filenames including paths"
    (is (= true  (probable-license-file? "/path/to/a/project/containing/a/pom.xml")))
    (is (= false (probable-license-file? "/a/different/path/to/some/NOTICES")))))

(deftest probable-license-files-tests
  (testing "Nil, empty, or blank directory"
    (is (nil?                                  (probable-license-files nil)))
    (is (thrown? java.io.FileNotFoundException (probable-license-files "")))
    (is (thrown? java.io.FileNotFoundException (probable-license-files "       ")))
    (is (thrown? java.io.FileNotFoundException (probable-license-files "\n")))
    (is (thrown? java.io.FileNotFoundException (probable-license-files "\t"))))
  (testing "Not a directory"
    (is (thrown? java.nio.file.NotDirectoryException (probable-license-files "deps.edn"))))
  (testing "A real directory"
      (is (= #{(io/file (str test-data-path "/asf-cat-1.0.12.pom"))
               (io/file (str test-data-path "/with-parent.pom"))
               (io/file (str test-data-path "/no-xml-ns.pom"))
               (io/file (str test-data-path "/simple.pom"))
               (io/file (str test-data-path "/CC-BY-4.0/LICENSE"))
               (io/file (str test-data-path "/MPL-2.0/LICENSE"))}
             (probable-license-files test-data-path)))))

(deftest file->ids-tests
  (testing "Nil, empty, or blank filename"
    (is (nil?                                  (file->ids nil)))
    (is (thrown? java.io.FileNotFoundException (file->ids "")))
    (is (thrown? java.io.FileNotFoundException (file->ids "       ")))
    (is (thrown? java.io.FileNotFoundException (file->ids "\n")))
    (is (thrown? java.io.FileNotFoundException (file->ids "\t"))))
  (testing "Non-existent files"
    (is (thrown? java.io.FileNotFoundException (file->ids "this_file_does_not_exist"))))
  (testing "License files"
;    (is (= #{"Apache-1.0"} (file->ids "https://www.apache.org/licenses/LICENSE-1.0")))    ; Note: this page incorrectly lists itself as Apache 1.1
    (is (= #{"CC-BY-4.0"}                               (file->ids (str test-data-path "/CC-BY-4.0/LICENSE"))))
    (is (= #{"MPL-2.0" "MPL-2.0-no-copyleft-exception"} (file->ids (str test-data-path "/MPL-2.0/LICENSE"))))
    (is (= #{"Apache-1.1"}                              (file->ids "https://www.apache.org/licenses/LICENSE-1.1")))
    (is (= #{"Apache-2.0"}                              (file->ids "https://www.apache.org/licenses/LICENSE-2.0.txt")))
    (is (= #{"EPL-1.0"}                                 (file->ids "https://www.eclipse.org/org/documents/epl-1.0/EPL-1.0.txt")))
    (is (= #{"EPL-2.0"}                                 (file->ids "https://www.eclipse.org/org/documents/epl-2.0/EPL-2.0.txt")))
    (is (= #{"CDDL-1.0"}                                (file->ids "https://spdx.org/licenses/CDDL-1.0.txt")))
    (is (= #{"CDDL-1.1"}                                (file->ids "https://spdx.org/licenses/CDDL-1.1.txt")))
    (is (= #{"GPL-1.0"}                                 (file->ids "https://www.gnu.org/licenses/gpl-1.0.txt")))
    (is (= #{"GPL-2.0"}                                 (file->ids "https://www.gnu.org/licenses/gpl-2.0.txt")))
    (is (= #{"GPL-3.0"}                                 (file->ids "https://www.gnu.org/licenses/gpl-3.0.txt")))
    (is (= #{"LGPL-2.0"}                                (file->ids "https://www.gnu.org/licenses/lgpl-2.0.txt")))
    (is (= #{"LGPL-2.1"}                                (file->ids "https://www.gnu.org/licenses/lgpl-2.1.txt")))
    (is (= #{"LGPL-3.0"}                                (file->ids "https://www.gnu.org/licenses/lgpl-3.0.txt")))
    (is (= #{"AGPL-3.0"}                                (file->ids "https://www.gnu.org/licenses/agpl-3.0.txt")))
    (is (= #{"Unlicense"}                               (file->ids "https://unlicense.org/UNLICENSE")))
    (is (= #{"WTFPL"}                                   (file->ids "http://www.wtfpl.net/txt/copying/"))))
  (testing "POM files"
    (is (= #{"Apache-2.0"}   (file->ids (str test-data-path "/simple.pom"))))
    (is (= #{"BSD-3-Clause"} (file->ids (str test-data-path "/no-xml-ns.pom"))))
    (is (= #{"Apache-2.0"}   (file->ids (str test-data-path "/asf-cat-1.0.12.pom"))))
    (is (= #{"Apache-2.0"}   (file->ids (str test-data-path "/with-parent.pom"))))))

(deftest dir->ids-tests
  (testing "Nil, empty, or blank directory name"
    (is (nil?                                  (dir->ids nil)))
    (is (thrown? java.io.FileNotFoundException (dir->ids "")))
    (is (thrown? java.io.FileNotFoundException (dir->ids "       ")))
    (is (thrown? java.io.FileNotFoundException (dir->ids "\n")))
    (is (thrown? java.io.FileNotFoundException (dir->ids "\t"))))
  (testing "Non-existent or invalid directory"
    (is (thrown? java.io.FileNotFoundException       (dir->ids "this_directory_does_not_exist")))
    (is (thrown? java.nio.file.NotDirectoryException (dir->ids "deps.edn"))))
  (testing "Valid directory"
    (is (= #{"Apache-2.0" "BSD-3-Clause" "MPL-2.0" "MPL-2.0-no-copyleft-exception" "CC-BY-4.0"} (dir->ids ".")))))

(deftest zip->ids-tests
  (testing "Nil, empty, or blank zip file name"
    (is (nil?                                      (zip->ids nil)))
    (is (thrown? java.io.FileNotFoundException     (zip->ids "")))            ; Note the hodgepodge of different thrown exception types here - java.util.zip is a mess!
    (is (thrown? java.nio.file.NoSuchFileException (zip->ids "       ")))
    (is (thrown? java.nio.file.NoSuchFileException (zip->ids "\n")))
    (is (thrown? java.nio.file.NoSuchFileException (zip->ids "\t"))))
  (testing "Non-existent zip file"
    (is (thrown? java.nio.file.NoSuchFileException (zip->ids "this_zip_file_does_not_exist"))))
  (testing "Invalid zip file"
    (is (thrown? java.util.zip.ZipException (zip->ids (str test-data-path "/bad.zip")))))
  (testing "Valid zip file"
    (is (= #{"Apache-2.0"} (zip->ids (str test-data-path "/good.zip"))))))

