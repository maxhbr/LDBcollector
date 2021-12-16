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

(ns lice-comb.deps-test
  (:require [clojure.test    :refer [deftest testing is]]
            [lice-comb.deps  :refer [dep->ids deps-licenses]]))

(deftest dep->ids-tests
  (testing "Nil deps"
    (is (nil? (dep->ids nil))))
  (testing "Valid deps - single license"
    (is (= #{"Apache-2.0"} (dep->ids ['com.github.pmonks/asf-cat {:deps/manifest :mvn :mvn/version "1.0.12"}])))
    (is (= #{"EPL-1.0"}    (dep->ids ['org.clojure/clojure {:deps/manifest :mvn :mvn/version "1.10.3"}]))))
  (testing "Valid deps - multi license"
    (is (= #{"GPL-2.0-with-classpath-exception" "MIT"} (dep->ids ['org.checkerframework/checker-compat-qual {:deps/manifest :mvn :mvn/version "2.5.5"}])))))


