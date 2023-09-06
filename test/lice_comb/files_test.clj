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
            [lice-comb.test-boilerplate :refer [fixture valid=]]
            [lice-comb.files            :refer [init! probable-license-file? probable-license-files file->expressions dir->expressions zip->expressions]]))

(use-fixtures :once fixture)

(def test-data-path "./test/lice_comb/data")

(deftest init!-tests
  (testing "Nil response"
    (is (nil? (init!)))))

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
    (is (= false (probable-license-file? "/a/different/path/to/some/NOTICES")))
    (is (= true  (probable-license-file? "https://repo1.maven.org/maven2/org/activecomponents/jadex/jadex-kernel-component/3.0.117/jadex-kernel-component-3.0.117.pom")))))

(deftest probable-license-files-tests
  (testing "Nil, empty, or blank directory"
    (is (nil? (probable-license-files nil)))
    (is (nil? (probable-license-files "")))
    (is (nil? (probable-license-files "       ")))
    (is (nil? (probable-license-files "\n")))
    (is (nil? (probable-license-files "\t"))))
  (testing "Doesn't exist"
    (is (nil? (probable-license-files "THIS_DIRECTORY_DOESNT_EXIST"))))
  (testing "Not a directory"
    (is (nil? (probable-license-files "deps.edn"))))
  (testing "A real directory"
      (is (= #{(io/file (str test-data-path "/asf-cat-1.0.12.pom"))
               (io/file (str test-data-path "/with-parent.pom"))
               (io/file (str test-data-path "/no-xml-ns.pom"))
               (io/file (str test-data-path "/simple.pom"))
               (io/file (str test-data-path "/complex.pom"))
               (io/file (str test-data-path "/CC-BY-4.0/LICENSE"))
               (io/file (str test-data-path "/MPL-2.0/LICENSE"))}
             (probable-license-files test-data-path)))))

(deftest file->expressions-tests
  (testing "Nil, empty, or blank filename"
    (is (nil? (file->expressions  nil)))
    (is (nil? (file->expressions  "")))
    (is (nil? (file->expressions  "       ")))
    (is (nil? (file->expressions  "\n")))
    (is (nil? (file->expressions  "\t"))))
  (testing "Non-existent files"
    (is (nil? (file->expressions  "this_file_does_not_exist"))))
  (testing "Handed a directory"
    (is (nil? (file->expressions "."))))
  (testing "Files on disk"
;    (is (= #{"CC-BY-4.0"} (file->expressions  (str test-data-path "/CC-BY-4.0/LICENSE"))))  ; Failing due to https://github.com/spdx/license-list-XML/issues/1960
    (is (valid= #{"MPL-2.0"}   (file->expressions  (str test-data-path "/MPL-2.0/LICENSE")))))
  (testing "URLs"
    (is (valid= #{"Apache-2.0"} (file->expressions  "https://www.apache.org/licenses/LICENSE-2.0.txt")))
    (is (valid= #{"Apache-2.0"} (file->expressions  (io/as-url "https://www.apache.org/licenses/LICENSE-2.0.txt")))))
  (testing "InputStreams"
    (is (thrown? clojure.lang.ExceptionInfo (with-open [is (io/input-stream "https://www.apache.org/licenses/LICENSE-2.0.txt")] (file->expressions  is))))
    (is (valid= #{"Apache-2.0"} (with-open [is (io/input-stream "https://www.apache.org/licenses/LICENSE-2.0.txt")]                  (file->expressions  is "LICENSE_2.0.txt")))))
  (testing "POM files"
    (is (valid= #{"Apache-2.0"}   (file->expressions  (str test-data-path "/simple.pom"))))
    (is (valid= #{"BSD-3-Clause"} (file->expressions  (str test-data-path "/no-xml-ns.pom"))))
    (is (valid= #{"Apache-2.0"}   (file->expressions  (str test-data-path "/asf-cat-1.0.12.pom"))))
    (is (valid= #{"Apache-2.0"}   (file->expressions  (str test-data-path "/with-parent.pom"))))))

(deftest zip->expressions-tests
  (testing "Nil, empty, or blank zip file name"
    (is (nil? (zip->expressions nil)))
    (is (nil? (zip->expressions "")))
    (is (nil? (zip->expressions "       ")))
    (is (nil? (zip->expressions "\n")))
    (is (nil? (zip->expressions "\t"))))
  (testing "Non-existent zip file"
    (is (nil? (zip->expressions "this_zip_file_does_not_exist"))))
  (testing "Handed a directory"
    (is (nil? (file->expressions "."))))
  (testing "Invalid zip file"
    (is (thrown? java.util.zip.ZipException (zip->expressions (str test-data-path "/bad.zip")))))
  (testing "Valid zip file"
    (is (valid= #{"Apache-2.0"}        (zip->expressions (str test-data-path "/good.zip"))))
    (is (valid= #{"AGPL-3.0-or-later"} (zip->expressions (str test-data-path "/pom-in-a-zip.zip"))))))

(deftest dir->expressions-tests
  (testing "Nil, empty, or blank directory name"
    (is (nil? (dir->expressions  nil)))
    (is (nil? (dir->expressions  "")))
    (is (nil? (dir->expressions  "       ")))
    (is (nil? (dir->expressions  "\n")))
    (is (nil? (dir->expressions  "\t"))))
  (testing "Non-existent or invalid directory"
    (is (nil? (dir->expressions  "this_directory_does_not_exist")))
    (is (nil? (dir->expressions  "deps.edn"))))
  (testing "Valid directory"
    (is (valid= ;#{"GPL-2.0-only WITH Classpath-exception-2.0" "BSD-3-Clause" "Apache-2.0" "Unlicense AND CC0-1.0" "MIT" "MPL-2.0" "CC-BY-4.0"}  ; CC-BY-4.0 failing due to https://github.com/spdx/license-list-XML/issues/1960
                #{"GPL-2.0-only WITH Classpath-exception-2.0" "BSD-3-Clause" "Apache-2.0" "Unlicense AND CC0-1.0" "MIT" "MPL-2.0"}
                (dir->expressions "."))))
  (testing "Valid directory - include ZIP compressed files"
    (is (valid= ;#{"GPL-2.0-only WITH Classpath-exception-2.0" "BSD-3-Clause" "Apache-2.0" "Unlicense AND CC0-1.0" "MIT" "MPL-2.0" "CC-BY-4.0" "AGPL-3.0-or-later"}  ; CC-BY-4.0 failing due to https://github.com/spdx/license-list-XML/issues/1960
                #{"GPL-2.0-only WITH Classpath-exception-2.0" "BSD-3-Clause" "Apache-2.0" "Unlicense AND CC0-1.0" "MIT" "MPL-2.0" "AGPL-3.0-or-later"}
                (dir->expressions  "." {:include-zips? true})))))
