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
  (:require [clojure.test               :refer [deftest testing is use-fixtures]]
            [lice-comb.test-boilerplate :refer [fixture]]
            [lice-comb.maven            :refer [pom->ids]]))

(use-fixtures :once fixture)

(def test-data-path "./test/lice_comb/data")

(deftest pom->ids-tests
  (testing "Nil pom"
    (is (nil? (pom->ids nil))))
  (testing "Invalid filenames"
    (is (thrown? java.io.FileNotFoundException         (pom->ids "")))
    (is (thrown? java.io.FileNotFoundException         (pom->ids "      ")))
    (is (thrown? java.io.FileNotFoundException         (pom->ids "\t")))
    (is (thrown? java.io.FileNotFoundException         (pom->ids "\n")))
    (is (thrown? java.io.FileNotFoundException         (pom->ids "this-file-doesnt-exist.pom")))
    (is (thrown? java.io.FileNotFoundException         (pom->ids "./this/path/and/file/doesnt/exist.pom"))))
  (testing "Synthetic pom files"
    (is (= #{"Apache-2.0"}                             (pom->ids (str test-data-path "/simple.pom"))))
    (is (= #{"BSD-3-Clause"}                           (pom->ids (str test-data-path "/no-xml-ns.pom")))))
  (testing "Real pom files - local"
    (is (= #{"Apache-2.0"}                             (pom->ids (str test-data-path "/asf-cat-1.0.12.pom")))))
  (testing "Real pom files - remote"
    (is (= #{"Apache-2.0"}                             (pom->ids "https://repo1.maven.org/maven2/software/amazon/ion/ion-java/1.0.2/ion-java-1.0.2.pom")))
    (is (= #{"LicenseRef-lice-comb-public-domain"}     (pom->ids "https://repo1.maven.org/maven2/aopalliance/aopalliance/1.0/aopalliance-1.0.pom")))           ; Note: non-SPDX
    (is (= #{"EPL-1.0"}                                (pom->ids "https://repo.clojars.org/org/clojure/clojure/1.4.0/clojure-1.4.0.pom")))
    (is (= #{"Apache-2.0"}                             (pom->ids "https://repo.clojars.org/com/github/pmonks/asf-cat/1.0.12/asf-cat-1.0.12.pom")))
    (is (= #{"Apache-2.0"}                             (pom->ids "https://repo.clojars.org/http-kit/http-kit/2.5.3/http-kit-2.5.3.pom")))
    (is (nil?                                          (pom->ids "https://repo.clojars.org/borkdude/sci.impl.reflector/0.0.1/sci.impl.reflector-0.0.1.pom")))   ; This project has no license information in its pom
    (is (= #{"CDDL-1.0"}                               (pom->ids "https://repo1.maven.org/maven2/javax/activation/activation/1.1.1/activation-1.1.1.pom")))
    (is (= #{"Plexus"}                                 (pom->ids "https://repo1.maven.org/maven2/org/jdom/jdom2/2.0.6.1/jdom2-2.0.6.1.pom")))                  ; See https://lists.linuxfoundation.org/pipermail/spdx-legal/2014-December/001280.html
    (is (= #{"GPL-3.0"}                                (pom->ids "https://repo1.maven.org/maven2/org/activecomponents/jadex/jadex-kernel-component/3.0.117/jadex-kernel-component-3.0.117.pom"))))
  (testing "Real pom files - remote - dual-licensed"
    (is (= #{"GPL-2.0-with-classpath-exception" "MIT"} (pom->ids "https://repo1.maven.org/maven2/org/checkerframework/checker-compat-qual/2.5.5/checker-compat-qual-2.5.5.pom"))))
  (testing "Synthetic pom files with licenses in parent - local"
    (is (= #{"Apache-2.0"}                             (pom->ids (str test-data-path "/with-parent.pom")))))
  (testing "Real pom files with licenses in parent - remote"
    (is (= #{"Apache-2.0"}                             (pom->ids "https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-core/1.12.69/aws-java-sdk-core-1.12.69.pom")))))
