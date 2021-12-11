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

(ns lice-comb.api-test
  (:require [clojure.test  :refer [deftest testing is]]
            [lice-comb.api :refer [from-name from-uri]]))

(println "\n☔️ Running tests on Clojure" (clojure-version) "/ JVM" (System/getProperty "java.version"))

(deftest from-name-tests
  (testing "Nil, empty or blank names"
    (is (nil? (from-name nil)))
    (is (nil? (from-name "")))
    (is (nil? (from-name "       ")))
    (is (nil? (from-name "\n")))
    (is (nil? (from-name "\t"))))
  (testing "Names that are SPDX license ids"
    (is (= ["Apache-2.0"]                       (from-name "Apache-2.0")))
    (is (= ["Apache-2.0"]                       (from-name "    Apache-2.0        ")))   ; Test whitespace
    (is (= ["GPL-2.0"]                          (from-name "GPL-2.0")))
    (is (= ["GPL-2.0-with-classpath-exception"] (from-name "GPL-2.0-with-classpath-exception")))
    (is (= ["AGPL-3.0"]                         (from-name "AGPL-3.0")))
    (is (= ["AGPL-3.0-only"]                    (from-name "AGPL-3.0-only")))
    (is (= ["CC-BY-SA-4.0"]                     (from-name "CC-BY-SA-4.0"))))
  (testing "Names that appear verbatim in the SPDX license list"
    (is (= ["Apache-2.0"]                       (from-name "Apache Software License, Version 2.0")))
    (is (= ["Apache-2.0"]                       (from-name "               Apache Software License, Version 2.0             ")))   ; Test whitespace
    (is (= ["AGPL-3.0"]                         (from-name "GNU Affero General Public License v3.0")))
    (is (= ["AGPL-3.0-only"]                    (from-name "GNU Affero General Public License v3.0 only")))
    (is (= ["CC-BY-SA-4.0"]                     (from-name "Creative Commons Attribution Share Alike 4.0 International")))
    (is (= ["GPL-2.0-with-classpath-exception"] (from-name "GNU General Public License v2.0 w/Classpath exception")))
    (is (= ["Apache-1.0"]                       (from-name "Apache Software License"))))
  (testing "Names that appear in licensey things, but aren't in the SPDX license list"
    (is (= ["Apache-2.0"]                       (from-name "Apache Software License v2.0")))
    (is (= ["Apache-2.0"]                       (from-name "Apache Software License 2.0")))
    (is (= ["Apache-2.0"]                       (from-name "Apache Software License Version 2.0")))
    (is (= ["Apache-2.0"]                       (from-name "Apache Software License v2")))
    (is (= ["Apache-2.0"]                       (from-name "Apache Software License 2")))
    (is (= ["Apache-2.0"]                       (from-name "Apache Software License Version 2")))))

(deftest from-uri-tests
  (testing "Nil, empty or blank uri"
    (is (nil? (from-uri nil)))
    (is (nil? (from-uri "")))
    (is (nil? (from-uri "       ")))
    (is (nil? (from-uri "\n")))
    (is (nil? (from-uri "\t"))))
  (testing "URIs that appear verbatim in the SPDX license list"
    (is (= "Apache-2.0"                       (from-uri "https://www.apache.org/licenses/LICENSE-2.0")))
    (is (= "Apache-2.0"                       (from-uri "               https://www.apache.org/licenses/LICENSE-2.0             ")))   ; Test whitespace
    (is (= "AGPL-3.0"                         (from-uri "https://www.gnu.org/licenses/agpl.txt")))
    (is (= "CC-BY-SA-4.0"                     (from-uri "https://creativecommons.org/licenses/by-sa/4.0/legalcode")))
    (is (= "GPL-2.0-with-classpath-exception" (from-uri "https://www.gnu.org/software/classpath/license.html"))))
  (testing "URIs that appear in licensey things, but aren't in the SPDX license list"
    (is (= "Apache-2.0"                       (from-uri "http://www.apache.org/licenses/LICENSE-2.0")))
    (is (= "Apache-2.0"                       (from-uri "https://www.apache.org/licenses/LICENSE-2.0.txt")))))
