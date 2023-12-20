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
            [lice-comb.test-boilerplate :refer [fixture valid=]]
            [lice-comb.impl.spdx        :as lcis]
            [lice-comb.maven            :refer [init! pom->expressions gav->expressions]]))

(use-fixtures :once fixture)

(def test-data-path "./test/lice_comb/data")

(deftest init!-tests
  (testing "Nil response"
    (is (nil? (init!)))))

(deftest pom->expressions-tests
  (testing "Nil pom"
    (is (nil? (pom->expressions nil))))
  (testing "Invalid filenames"
    (is (thrown? java.io.FileNotFoundException (pom->expressions "")))
    (is (thrown? java.io.FileNotFoundException (pom->expressions "      ")))
    (is (thrown? java.io.FileNotFoundException (pom->expressions "\t")))
    (is (thrown? java.io.FileNotFoundException (pom->expressions "\n")))
    (is (thrown? java.io.FileNotFoundException (pom->expressions "this-file-doesnt-exist.pom")))
    (is (thrown? java.io.FileNotFoundException (pom->expressions "./this/path/and/file/doesnt/exist.pom"))))
  (testing "Synthetic pom files"
    (is (valid= #{"Apache-2.0"}                (pom->expressions (str test-data-path "/simple.pom"))))
    (is (valid= #{"BSD-3-Clause"}              (pom->expressions (str test-data-path "/no-xml-ns.pom"))))
    (is (valid= #{"Apache-2.0" "MIT" "GPL-2.0-only WITH Classpath-exception-2.0" "BSD-3-Clause" "Unlicense AND CC0-1.0"} (pom->expressions (str test-data-path "/complex.pom")))))
  (testing "Real pom files - local"
    (is (valid= #{"Apache-2.0"}                (pom->expressions (str test-data-path "/asf-cat-1.0.12.pom")))))
  (testing "Real pom files - remote"
    (is (valid= #{"Apache-2.0"}                (pom->expressions "https://repo1.maven.org/maven2/software/amazon/ion/ion-java/1.0.2/ion-java-1.0.2.pom")))
    (is (valid= #{(lcis/public-domain)}        (pom->expressions "https://repo1.maven.org/maven2/aopalliance/aopalliance/1.0/aopalliance-1.0.pom")))           ; Note: non-SPDX
    (is (valid= #{"EPL-1.0"}                   (pom->expressions "https://repo.clojars.org/org/clojure/clojure/1.4.0/clojure-1.4.0.pom")))
    (is (valid= #{"Apache-2.0"}                (pom->expressions "https://repo.clojars.org/com/github/pmonks/asf-cat/1.0.12/asf-cat-1.0.12.pom")))
    (is (valid= #{"Apache-2.0"}                (pom->expressions "https://repo.clojars.org/http-kit/http-kit/2.5.3/http-kit-2.5.3.pom")))
    (is (nil?                                  (pom->expressions "https://repo.clojars.org/borkdude/sci.impl.reflector/0.0.1/sci.impl.reflector-0.0.1.pom")))   ; This project has no license information in its pom
    (is (valid= #{"CDDL-1.0"}                  (pom->expressions "https://repo1.maven.org/maven2/javax/activation/activation/1.1.1/activation-1.1.1.pom")))
    (is (valid= #{"Plexus"}                    (pom->expressions "https://repo1.maven.org/maven2/org/jdom/jdom2/2.0.6.1/jdom2-2.0.6.1.pom")))                  ; See https://lists.linuxfoundation.org/pipermail/spdx-legal/2014-December/001280.html
    (is (valid= #{"GPL-3.0-only"}              (pom->expressions "https://repo1.maven.org/maven2/org/activecomponents/jadex/jadex-kernel-component/3.0.117/jadex-kernel-component-3.0.117.pom"))))
  (testing "Real pom files - remote - dual-licensed"
    (is (valid= #{"GPL-2.0-only WITH Classpath-exception-2.0" "MIT"} (pom->expressions "https://repo1.maven.org/maven2/org/checkerframework/checker-compat-qual/2.5.5/checker-compat-qual-2.5.5.pom"))))
  (testing "Real pom files - remote - malformed"
    (is (thrown? javax.xml.stream.XMLStreamException (pom->expressions "https://repo1.maven.org/maven2/org/codehaus/plexus/plexus-container-default/1.0-alpha-9-stable-1/plexus-container-default-1.0-alpha-9-stable-1.pom"))))
  (testing "Synthetic pom files with licenses in parent - local"
    (is (valid= #{"Apache-2.0"}                (pom->expressions (str test-data-path "/with-parent.pom")))))
  (testing "Real pom files with licenses in parent - remote"
    (is (valid= #{"Apache-2.0"}                (pom->expressions "https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-core/1.12.69/aws-java-sdk-core-1.12.69.pom")))))

(deftest gav->expressions-tests
  (testing "Nil GAV"
    (is (nil? (gav->expressions nil nil)))
    (is (nil? (gav->expressions nil nil nil))))
  (testing "Not null but invalid GAVs"
    (is (nil? (gav->expressions "invalid" "invalid")))
    (is (nil? (gav->expressions "invalid" "invalid" "invalid"))))
  (testing "Valid GAs"
    (is (valid= #{"EPL-2.0"}    (gav->expressions "quil"                "quil")))          ; Clojars
    (is (valid= #{"EPL-1.0"}    (gav->expressions "org.clojure"         "clojure")))       ; Maven Central
    (is (valid= #{"Apache-2.0"} (gav->expressions "org.springframework" "spring-core"))))  ; Maven Central
  (testing "Valid GAVs"
    (is (valid= #{"EPL-2.0"}    (gav->expressions "quil"                "quil"        "4.3.1323")))                   ; Clojars
    (is (valid= #{"EPL-2.0"}    (gav->expressions "quil"                "quil"        "4.3.1426-5368295-SNAPSHOT")))  ; Clojars, SNAPSHOT
    (is (valid= #{"EPL-1.0"}    (gav->expressions "org.clojure"         "clojure"     "1.11.1")))                     ; Maven Central
    (is (valid= #{"EPL-1.0"}    (gav->expressions "org.clojure"         "clojure"     "1.12.0-alpha5")))              ; Maven Central, custom suffix
    (is (valid= #{"Apache-2.0"} (gav->expressions "org.springframework" "spring-core" "6.1.0")))))                    ; Maven Central
