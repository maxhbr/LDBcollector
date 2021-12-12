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
            [lice-comb.maven :refer [from-pom]]))

(deftest from-pom-tests
  (testing "Nil pom"
    (is (nil? (from-pom nil))))
  (testing "Invalid filenames"
    (is (thrown? java.io.FileNotFoundException (from-pom "")))
    (is (thrown? java.io.FileNotFoundException (from-pom "      ")))
    (is (thrown? java.io.FileNotFoundException (from-pom "\t")))
    (is (thrown? java.io.FileNotFoundException (from-pom "\n")))
    (is (thrown? java.io.FileNotFoundException (from-pom "this-file-doesnt-exist.pom")))
    (is (thrown? java.io.FileNotFoundException (from-pom "./this/path/and/file/doesnt/exist.pom"))))
  )
