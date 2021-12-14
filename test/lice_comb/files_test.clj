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
  (:require [clojure.test    :refer [deftest testing is]]
            [clojure.java.io :as io]
            [lice-comb.files :refer [probable-license-file? probable-license-files file->ids dir->ids zip->ids]]))

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
    (is (= [(io/file "./LICENSE")] (probable-license-files ".")))))

(deftest file->ids-tests
  (testing "Nil, empty, or blank file"
    (is (nil?                                  (file->ids nil)))
    (is (thrown? java.io.FileNotFoundException (file->ids "")))
    (is (thrown? java.io.FileNotFoundException (file->ids "       ")))
    (is (thrown? java.io.FileNotFoundException (file->ids "\n")))
    (is (thrown? java.io.FileNotFoundException (file->ids "\t")))))


