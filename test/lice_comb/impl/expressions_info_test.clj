;
; Copyright © 2023 Peter Monks
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

(ns lice-comb.impl.expressions-info-test
  (:require [clojure.test                    :refer [deftest testing is use-fixtures]]
            [lice-comb.test-boilerplate      :refer [fixture]]
            [lice-comb.impl.expressions-info :refer [prepend-source merge-maps]]))

(use-fixtures :once fixture)

(def md1 {
  "Apache-2.0" '({:type :concluded :confidence :medium :strategy :regex-matching                     :source ("Apache Software Licence v2.0")})
  "MIT"        '({:type :concluded :confidence :high   :strategy :spdx-listed-identifier-exact-match :source ("MIT")})})

(def md2 {
  "Apache-2.0"   '({:type :concluded :confidence :low  :strategy :regex-matching :source ("Apache style license")})
  "BSD-4-Clause" '({:type :concluded :confidence :low  :strategy :regex-matching :source ("BSD")})})

(def md3 {
  "Apache-2.0"       '({:type :concluded :confidence :low  :strategy :regex-matching :source ("Apache style license")}
                       {:type :concluded :confidence :medium :strategy :spdx-listed-identifier-case-insensitive-match :source ("apache-2.0")}
                       {:type :declared :strategy :spdx-listed-identifier-exact-match :source ("Apache-2.0")})
  "GPL-3.0-or-later" '({:type :concluded :confidence :low  :strategy :regex-matching :source ("GNU General Public License 3.0 or later")})})

(def mds (list md1 md2 md3))

(deftest prepend-source-tests
  (testing "nil/empty/blank"
    (is (nil? (prepend-source nil nil)))
    (is (= {} (prepend-source nil {})))
    (is (nil? (prepend-source "" nil)))
    (is (= {} (prepend-source "" {}))))
  (testing "non-nil metadata that isn't lice-comb specific"
    (is (= {:a "a"} (prepend-source "foo" {:a "a"}))))
  (testing "non-nil metadata that is lice-comb specific"
    (is (= {"Apache-2.0" '({:type :concluded :confidence :medium :strategy :regex-matching                     :source ("pom.xml" "Apache Software Licence v2.0")})
            "MIT"        '({:type :concluded :confidence :high   :strategy :spdx-listed-identifier-exact-match :source ("pom.xml" "MIT")})}
           (prepend-source "pom.xml" md1)))
    (is (= {"Apache-2.0" '({:type :concluded :confidence :medium :strategy :regex-matching                     :source ("library.jar" "pom.xml" "Apache Software Licence v2.0")})
            "MIT"        '({:type :concluded :confidence :high   :strategy :spdx-listed-identifier-exact-match :source ("library.jar" "pom.xml" "MIT")})}
           (prepend-source "library.jar" (prepend-source "pom.xml" md1))))
    (is (= {"Apache-2.0"       '({:type :concluded :confidence :low  :strategy :regex-matching :source ("pom.xml" "Apache style license")}
                                 {:type :concluded :confidence :medium :strategy :spdx-listed-identifier-case-insensitive-match :source ("pom.xml" "apache-2.0")}
                                 {:type :declared :strategy :spdx-listed-identifier-exact-match :source ("pom.xml" "Apache-2.0")})
            "GPL-3.0-or-later" '({:type :concluded :confidence :low  :strategy :regex-matching :source ("pom.xml" "GNU General Public License 3.0 or later")})}
           (prepend-source "pom.xml" md3)))))

(deftest merge-maps-tests
  (testing "nil/empty"
    (is (nil? (merge-maps)))
    (is (nil? (merge-maps nil))))
  (testing "identity"
    (is (= md1 (merge-maps md1))))
  (testing "merges"
    (is (= {"Apache-2.0"   '({:type :concluded :confidence :medium :strategy :regex-matching :source ("Apache Software Licence v2.0")}
                             {:type :concluded :confidence :low  :strategy :regex-matching :source ("Apache style license")})
            "MIT"          '({:type :concluded :confidence :high   :strategy :spdx-listed-identifier-exact-match :source ("MIT")})
            "BSD-4-Clause" '({:type :concluded :confidence :low  :strategy :regex-matching :source ("BSD")})}
           (merge-maps md1 md2)))
    (is (= {"Apache-2.0"       '({:type :concluded :confidence :low  :strategy :regex-matching :source ("Apache style license")}  ; Note de-duping
                                 {:type :concluded :confidence :medium :strategy :spdx-listed-identifier-case-insensitive-match :source ("apache-2.0")}
                                 {:type :declared :strategy :spdx-listed-identifier-exact-match :source ("Apache-2.0")})
            "BSD-4-Clause"     '({:type :concluded :confidence :low  :strategy :regex-matching :source ("BSD")})
            "GPL-3.0-or-later" '({:type :concluded :confidence :low  :strategy :regex-matching :source ("GNU General Public License 3.0 or later")})}
           (merge-maps md2 md3)))
    (is (= {"Apache-2.0"       '({:type :concluded :confidence :medium :strategy :regex-matching :source ("Apache Software Licence v2.0")}
                                 {:type :concluded :confidence :low  :strategy :regex-matching :source ("Apache style license")}  ; Note de-duping
                                 {:type :concluded :confidence :medium :strategy :spdx-listed-identifier-case-insensitive-match :source ("apache-2.0")}
                                 {:type :declared :strategy :spdx-listed-identifier-exact-match :source ("Apache-2.0")})
            "MIT"              '({:type :concluded :confidence :high   :strategy :spdx-listed-identifier-exact-match :source ("MIT")})
            "BSD-4-Clause"     '({:type :concluded :confidence :low  :strategy :regex-matching :source ("BSD")})
            "GPL-3.0-or-later" '({:type :concluded :confidence :low  :strategy :regex-matching :source ("GNU General Public License 3.0 or later")})}
           (apply merge-maps mds)))))
