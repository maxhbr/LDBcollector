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

(ns lice-comb.maven-test
  (:require [clojure.test    :refer [deftest testing is]]
            [lice-comb.maven :refer [pom->ids]]))

(def test-data-path "./test/lice_comb/data")

(deftest pom->ids-tests
  (testing "Nil pom"
    (is (nil? (pom->ids nil))))
  (testing "Invalid filenames"
    (is (thrown? java.io.FileNotFoundException (pom->ids "")))
    (is (thrown? java.io.FileNotFoundException (pom->ids "      ")))
    (is (thrown? java.io.FileNotFoundException (pom->ids "\t")))
    (is (thrown? java.io.FileNotFoundException (pom->ids "\n")))
    (is (thrown? java.io.FileNotFoundException (pom->ids "this-file-doesnt-exist.pom")))
    (is (thrown? java.io.FileNotFoundException (pom->ids "./this/path/and/file/doesnt/exist.pom"))))
  (testing "Synthetic pom files"
    (is (= ["Apache-2.0"]   (pom->ids (str test-data-path "/simple.pom"))))
    (is (= ["BSD-3-Clause"] (pom->ids (str test-data-path "/no-xml-ns.pom")))))
  (testing "Real pom files - local"
    (is (= ["Apache-2.0"] (pom->ids (str test-data-path "/asf-cat-1.0.12.pom")))))
  (testing "Real pom files - remote"
    (is (= ["Apache-2.0"] (pom->ids "https://repo1.maven.org/maven2/software/amazon/ion/ion-java/1.0.2/ion-java-1.0.2.pom"))))
  (testing "Synthetic pom files with licenses in parent - local"
    (is (= ["Apache-2.0"] (pom->ids (str test-data-path "/with-parent.pom")))))
  (testing "Real pom files with licenses in parent - remote"
    (is (= ["Apache-2.0"] (pom->ids "https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-core/1.12.69/aws-java-sdk-core-1.12.69.pom")))))
